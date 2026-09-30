import os
import re

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QSlider,
    QSizePolicy,
    QFrame
)

from PyQt6.QtCore import (
    Qt,
    QUrl,
    QTimer,
    QEvent
)

from PyQt6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput
)

from PyQt6.QtMultimediaWidgets import QVideoWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Bölüm Listesi")
        self.resize(1200, 700)

        self.video_extensions = {
            ".mkv",
            ".mp4",
            ".avi",
            ".mov",
            ".webm"
        }

        self.videos = []
        self.current_episode_row = -1
        self.is_fullscreen = False

        # -------------------------------------------------
        # ANA WIDGET
        # -------------------------------------------------

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # -------------------------------------------------
        # VIDEO TARAFI
        # -------------------------------------------------

        self.video_container = QWidget()

        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_layout.setSpacing(0)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.video_layout.addWidget(self.video_widget)

        # -------------------------------------------------
        # VIDEO LABEL
        # -------------------------------------------------

        self.video_label = QLabel("Henüz video seçilmedi")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: white;
                font-size: 24px;
            }
        """)

        self.video_label.setParent(self.video_widget)
        self.video_label.raise_()

        # -------------------------------------------------
        # SONRAKİ BÖLÜM YAZISI
        # -------------------------------------------------

        self.next_episode_label = QLabel("")
        self.next_episode_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.next_episode_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 190);
                color: white;
                font-size: 20px;
                padding: 15px;
                border-radius: 10px;
            }
        """)

        self.next_episode_label.setParent(self.video_widget)
        self.next_episode_label.hide()
        self.next_episode_label.raise_()

        # -------------------------------------------------
        # KONTROLLER
        # -------------------------------------------------

        self.controls_frame = QFrame()
        self.controls_frame.setStyleSheet("""
            QFrame {
                background-color: #181818;
            }

            QPushButton {
                background-color: #292929;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
            }

            QSlider::groove:horizontal {
                height: 5px;
                background: #444;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
                background: white;
            }

            QLabel {
                color: white;
            }
        """)

        self.controls_layout = QHBoxLayout(self.controls_frame)
        self.controls_layout.setContentsMargins(8, 8, 8, 8)
        self.controls_layout.setSpacing(8)

        # Geri
        self.back_button = QPushButton("⏪ 10")
        self.controls_layout.addWidget(self.back_button)

        # Oynat / durdur
        self.play_button = QPushButton("▶")
        self.controls_layout.addWidget(self.play_button)

        # İleri
        self.forward_button = QPushButton("10 ⏩")
        self.controls_layout.addWidget(self.forward_button)

        # Pozisyon slider
        self.position_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.position_slider.setRange(0, 0)

        self.controls_layout.addWidget(
            self.position_slider,
            1
        )

        # Zaman
        self.time_label = QLabel("00:00 / 00:00")
        self.controls_layout.addWidget(self.time_label)

        # Ses
        self.mute_button = QPushButton("🔊")
        self.controls_layout.addWidget(self.mute_button)

        # Ses slider
        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setMaximumWidth(120)

        self.controls_layout.addWidget(
            self.volume_slider
        )

        # Tam ekran
        self.fullscreen_button = QPushButton("⛶")
        self.controls_layout.addWidget(
            self.fullscreen_button
        )

        self.video_layout.addWidget(
            self.controls_frame
        )

        # -------------------------------------------------
        # BUTONLAR KLAVYE ODAĞI ALMASIN
        # -------------------------------------------------

        buttons = (
            self.back_button,
            self.play_button,
            self.forward_button,
            self.mute_button,
            self.fullscreen_button
        )

        for button in buttons:
            button.setFocusPolicy(
                Qt.FocusPolicy.NoFocus
            )

        # Sliderlar da klavye odağı almasın
        self.position_slider.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.volume_slider.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        # -------------------------------------------------
        # BÖLÜM LİSTESİ
        # -------------------------------------------------

        self.episode_container = QWidget()

        self.episode_container.setMinimumWidth(280)
        self.episode_container.setMaximumWidth(400)

        self.episode_layout = QVBoxLayout(
            self.episode_container
        )

        self.episode_layout.setContentsMargins(
            10, 10, 10, 10
        )

        self.episode_layout.setSpacing(8)

        # Klasör seç
        self.folder_button = QPushButton(
            "📁 Klasör Seç"
        )

        self.folder_button.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.episode_layout.addWidget(
            self.folder_button
        )

        # Bölüm listesi
        self.episode_list = QListWidget()

        self.episode_list.setStyleSheet("""
            QListWidget {
                background-color: #181818;
                color: white;
                border: none;
            }

            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
            }

            QListWidget::item:hover {
                background-color: #292929;
            }

            QListWidget::item:selected {
                background-color: #3a3a3a;
            }
        """)

        self.episode_layout.addWidget(
            self.episode_list
        )

        # -------------------------------------------------
        # ANA LAYOUT
        # -------------------------------------------------

        self.main_layout.addWidget(
            self.video_container,
            1
        )

        self.main_layout.addWidget(
            self.episode_container
        )

        # -------------------------------------------------
        # MEDIA PLAYER
        # -------------------------------------------------

        self.player = QMediaPlayer(self)

        self.audio_output = QAudioOutput(self)

        self.audio_output.setVolume(1.0)

        self.player.setAudioOutput(
            self.audio_output
        )

        self.player.setVideoOutput(
            self.video_widget
        )

        # -------------------------------------------------
        # FULLSCREEN TIMER
        # -------------------------------------------------

        self.fullscreen_timer = QTimer(self)
        self.fullscreen_timer.setSingleShot(True)

        self.fullscreen_timer.timeout.connect(
            self.hide_fullscreen_controls
        )

        # -------------------------------------------------
        # SİNYALLER
        # -------------------------------------------------

        self.folder_button.clicked.connect(
            self.select_folder
        )

        self.episode_list.itemDoubleClicked.connect(
            self.play_episode
        )

        self.back_button.clicked.connect(
            self.seek_backward
        )

        self.play_button.clicked.connect(
            self.toggle_play
        )

        self.forward_button.clicked.connect(
            self.seek_forward
        )

        self.position_slider.sliderMoved.connect(
            self.set_position
        )

        self.mute_button.clicked.connect(
            self.toggle_mute
        )

        self.volume_slider.valueChanged.connect(
            self.change_volume
        )

        self.fullscreen_button.clicked.connect(
            self.toggle_fullscreen
        )

        self.player.positionChanged.connect(
            self.position_changed
        )

        self.player.durationChanged.connect(
            self.duration_changed
        )

        self.player.playbackStateChanged.connect(
            self.playback_state_changed
        )

        self.player.mediaStatusChanged.connect(
            self.media_status_changed
        )

        # -------------------------------------------------
        # VIDEO MOUSE EVENT
        # -------------------------------------------------

        self.video_widget.installEventFilter(self)

        self.video_click_pending = False

        # Başlangıç
        self.video_label.show()

    # =====================================================
    # KLASÖR SEÇ
    # =====================================================

    def select_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Video klasörü seç"
        )

        if not folder:
            return

        self.load_videos(folder)

    # =====================================================
    # VIDEOLARI YÜKLE
    # =====================================================

    def load_videos(self, folder):

        self.videos.clear()
        self.episode_list.clear()

        for filename in os.listdir(folder):

            full_path = os.path.join(
                folder,
                filename
            )

            if not os.path.isfile(full_path):
                continue

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in self.video_extensions:
                continue

            match = re.match(
                r"^(\d+)\.",
                filename
            )

            if not match:
                continue

            episode_number = int(
                match.group(1)
            )

            filename_without_extension = os.path.splitext(
                filename
            )[0]

            clean_name = re.sub(
                r"^\d+\.",
                "",
                filename_without_extension
            )

            clean_name = clean_name.replace(
                "..",
                "."
            )

            clean_name = clean_name.strip(
                " ."
            )

            self.videos.append({
                "number": episode_number,
                "name": clean_name,
                "path": full_path
            })

        # Numaraya göre sırala
        self.videos.sort(
            key=lambda video: video["number"]
        )

        # Listeye ekle
        for video in self.videos:

            text = (
                f"{video['number']}. Bölüm    "
                f"{video['name']}"
            )

            item = QListWidgetItem(text)

            item.setData(
                Qt.ItemDataRole.UserRole,
                video["path"]
            )

            self.episode_list.addItem(item)

        self.current_episode_row = -1

        self.video_label.setText(
            "Henüz video seçilmedi"
        )

        self.video_label.show()

    # =====================================================
    # BÖLÜM OYNAT
    # =====================================================

    def play_episode(self, item):

        row = self.episode_list.row(item)

        if row < 0 or row >= len(self.videos):
            return

        self.current_episode_row = row

        self.update_selected_episode()

        video_path = self.videos[row]["path"]

        self.video_label.hide()

        self.player.setSource(
            QUrl.fromLocalFile(video_path)
        )

        self.player.play()

        self.play_button.setText("⏸")

    # =====================================================
    # SEÇİLİ BÖLÜMÜ GÖSTER
    # =====================================================

    def update_selected_episode(self):

        for row in range(
            self.episode_list.count()
        ):

            item = self.episode_list.item(row)

            video = self.videos[row]

            prefix = "> " if row == self.current_episode_row else ""

            item.setText(
                f"{prefix}"
                f"{video['number']}. Bölüm    "
                f"{video['name']}"
            )

    # =====================================================
    # OYNAT / DURDUR
    # =====================================================

    def toggle_play(self):

        if self.player.playbackState() == (
            QMediaPlayer.PlaybackState.PlayingState
        ):

            self.player.pause()

        else:

            if self.player.source().isEmpty():
                return

            self.player.play()

    # =====================================================
    # OYNATMA DURUMU
    # =====================================================

    def playback_state_changed(self, state):

        if state == (
            QMediaPlayer.PlaybackState.PlayingState
        ):

            self.play_button.setText("⏸")

        else:

            self.play_button.setText("▶")

    # =====================================================
    # 10 SANİYE GERİ
    # =====================================================

    def seek_backward(self):

        position = self.player.position()

        self.player.setPosition(
            max(0, position - 10000)
        )

    # =====================================================
    # 10 SANİYE İLERİ
    # =====================================================

    def seek_forward(self):

        position = self.player.position()

        duration = self.player.duration()

        self.player.setPosition(
            min(duration, position + 10000)
        )

    # =====================================================
    # POZİSYON
    # =====================================================

    def position_changed(self, position):

        if not self.position_slider.isSliderDown():

            self.position_slider.setValue(
                position
            )

        self.update_time_label()

    # =====================================================
    # SÜRE
    # =====================================================

    def duration_changed(self, duration):

        self.position_slider.setRange(
            0,
            duration
        )

        self.update_time_label()

    # =====================================================
    # SLIDER'DAN POZİSYON
    # =====================================================

    def set_position(self, position):

        self.player.setPosition(
            position
        )

    # =====================================================
    # ZAMAN YAZISI
    # =====================================================

    def update_time_label(self):

        position = self.player.position()
        duration = self.player.duration()

        self.time_label.setText(
            f"{self.format_time(position)} / "
            f"{self.format_time(duration)}"
        )

    # =====================================================
    # ZAMAN FORMAT
    # =====================================================

    def format_time(self, milliseconds):

        total_seconds = milliseconds // 1000

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        seconds = total_seconds % 60

        if hours > 0:

            return (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        return (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    # =====================================================
    # SES
    # =====================================================

    def change_volume(self, value):

        self.audio_output.setVolume(
            value / 100
        )

        if value == 0:

            self.mute_button.setText("🔇")

        elif value < 50:

            self.mute_button.setText("🔉")

        else:

            self.mute_button.setText("🔊")

        if value > 0:
            self.audio_output.setMuted(False)

    # =====================================================
    # MUTE
    # =====================================================

    def toggle_mute(self):

        muted = self.audio_output.isMuted()

        self.audio_output.setMuted(
            not muted
        )

        if muted:

            value = self.volume_slider.value()

            if value == 0:
                self.volume_slider.setValue(50)

            self.mute_button.setText("🔊")

        else:

            self.mute_button.setText("🔇")

    # =====================================================
    # MEDIA STATUS
    # =====================================================

    def media_status_changed(self, status):

        if status != (
            QMediaPlayer.MediaStatus.EndOfMedia
        ):
            return

        next_row = (
            self.current_episode_row + 1
        )

        if next_row >= len(self.videos):

            return

        next_video = self.videos[next_row]

        self.next_episode_label.setText(
            "▶ Sonraki bölüm:\n"
            f"{next_video['number']}. Bölüm — "
            f"{next_video['name']}"
        )

        self.next_episode_label.adjustSize()

        self.next_episode_label.move(
            (self.video_widget.width() -
             self.next_episode_label.width()) // 2,

            (self.video_widget.height() -
             self.next_episode_label.height()) // 2
        )

        self.next_episode_label.show()
        self.next_episode_label.raise_()

        QTimer.singleShot(
            2500,
            self.next_episode_label.hide
        )

        item = self.episode_list.item(
            next_row
        )

        if item:
            self.play_episode(item)

    # =====================================================
    # FULLSCREEN
    # =====================================================

    def toggle_fullscreen(self):

        if self.is_fullscreen:

            self.exit_fullscreen()

        else:

            self.enter_fullscreen()

    # =====================================================
    # FULLSCREEN'A GIR
    # =====================================================

    def enter_fullscreen(self):

        self.is_fullscreen = True

        self.episode_container.hide()

        self.showFullScreen()

        self.controls_frame.show()

        self.fullscreen_timer.start(
            5000
        )

        self.update_overlay_positions()

    # =====================================================
    # FULLSCREEN'DAN ÇIK
    # =====================================================

    def exit_fullscreen(self):

        self.is_fullscreen = False

        self.fullscreen_timer.stop()

        self.showNormal()

        self.episode_container.show()

        self.controls_frame.show()

        self.update_overlay_positions()

    # =====================================================
    # FULLSCREEN KONTROLLERİNİ GİZLE
    # =====================================================

    def hide_fullscreen_controls(self):

        if self.is_fullscreen:

            self.controls_frame.hide()

    # =====================================================
    # FULLSCREEN MOUSE HAREKETİ
    # =====================================================

    def eventFilter(self, obj, event):

        if obj == self.video_widget:

            if event.type() == QEvent.Type.MouseMove:

                if self.is_fullscreen:

                    y = event.position().y()

                    height = self.video_widget.height()

                    # Videonun alt kısmına gelindiyse
                    if y >= height - 150:

                        self.controls_frame.show()

                        self.fullscreen_timer.start(
                            5000
                        )

                    else:

                        if self.controls_frame.isVisible():

                            self.fullscreen_timer.start(
                                5000
                            )

            elif event.type() == QEvent.Type.MouseButtonRelease:

                if event.button() == (
                    Qt.MouseButton.LeftButton
                ):

                    self.video_click_pending = True

                    QTimer.singleShot(
                        220,
                        self.delayed_video_click
                    )

                    return True

            elif event.type() == QEvent.Type.MouseButtonDblClick:

                if event.button() == (
                    Qt.MouseButton.LeftButton
                ):

                    self.video_click_pending = False

                    self.toggle_fullscreen()

                    return True

        return super().eventFilter(
            obj,
            event
        )

    # =====================================================
    # TEK TIKLAMA
    # =====================================================

    def delayed_video_click(self):

        if self.video_click_pending:

            self.video_click_pending = False

            self.toggle_play()

    # =====================================================
    # KLAVYE KONTROLLERİ
    # =====================================================

    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key.Key_Space:

            self.toggle_play()

            event.accept()

            return

        if key == Qt.Key.Key_F:

            self.toggle_fullscreen()

            event.accept()

            return

        if key == Qt.Key.Key_Escape:

            if self.is_fullscreen:

                self.exit_fullscreen()

            event.accept()

            return

        if key == Qt.Key.Key_Left:

            self.seek_backward()

            event.accept()

            return

        if key == Qt.Key.Key_Right:

            self.seek_forward()

            event.accept()

            return

        super().keyPressEvent(event)

    # =====================================================
    # RESIZE
    # =====================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.update_overlay_positions()

    # =====================================================
    # OVERLAY POZİSYONLARI
    # =====================================================

    def update_overlay_positions(self):

        self.video_label.setGeometry(
            self.video_widget.rect()
        )

        self.next_episode_label.adjustSize()

        self.next_episode_label.move(
            (self.video_widget.width() -
             self.next_episode_label.width()) // 2,

            (self.video_widget.height() -
             self.next_episode_label.height()) // 2
        )

        self.video_label.raise_()

        if self.next_episode_label.isVisible():

            self.next_episode_label.raise_()

    # =====================================================
    # PENCERE KAPATILIRKEN
    # =====================================================

    def closeEvent(self, event):

        self.player.stop()

        event.accept()
