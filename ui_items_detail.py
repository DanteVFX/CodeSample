

# Third-party modules
import urllib.request
import json
from functools import partial
import cv2
import numpy as np
from PySide2 import QtWidgets, QtGui, QtCore

# Local modules
from api.auth import load_session


class ItemDetailWidget(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super(ItemDetailWidget, self).__init__(parent)

        self.cap = None
        self.video_url = None
        self.video_timer = QtCore.QTimer()
        self.video_timer.timeout.connect(self.play_video_frame)

        self.video_path_list = []
        self.selected_button = None
        self.button_list = []

        self.scroll_content = QtWidgets.QWidget()
        self.setWidget(self.scroll_content)
        self.setWidgetResizable(True)
        self.main_layout = QtWidgets.QVBoxLayout(self.scroll_content)

        # Nombre y descripción
        self.name_label = QtWidgets.QLabel("Item name")
        self.name_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: white;")
        self.description_label = QtWidgets.QLabel("Description")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: white;")
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.description_label)

        # Video + thumbnails
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.left_widget = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout(self.left_widget)

        self.video_label = QtWidgets.QLabel("Loading preview...")
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        self.left_layout.addWidget(self.video_label)

        self.right_scroll = QtWidgets.QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.thumbnail_container = QtWidgets.QWidget()
        self.thumbnail_layout = QtWidgets.QVBoxLayout(self.thumbnail_container)
        self.right_scroll.setWidget(self.thumbnail_container)

        self.horizontal_layout.addWidget(self.left_widget, stretch=4)
        self.horizontal_layout.addWidget(self.right_scroll, stretch=1)
        self.main_layout.addLayout(self.horizontal_layout)

        # Play/Pause/Stop controls
        self.play_btn = QtWidgets.QPushButton("▶")
        self.pause_btn = QtWidgets.QPushButton("⏸")
        self.stop_btn = QtWidgets.QPushButton("⏹")
        for btn in [self.play_btn, self.pause_btn, self.stop_btn]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "font-size: 18px; background-color: #3ad1ff; color: white; border-radius: 5px;")

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addStretch()
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()
        self.main_layout.addLayout(controls_layout)

        # Video resolution selector (combo box)
        self.variant_combo = QtWidgets.QComboBox()
        self.variant_combo.setStyleSheet(
            "background-color: #3E3E3E; color: white;")
        self.variant_combo.setMinimumWidth(200)
        self.variant_combo.addItem("Select Resolution")
        self.main_layout.addWidget(self.variant_combo)

        # Back button
        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.setStyleSheet(
            "background-color: gray; color: white; padding: 6px;")
        self.main_layout.addWidget(self.back_button)

        # Connect signals
        self.play_btn.clicked.connect(self.start_video)
        self.pause_btn.clicked.connect(self.pause_video)
        self.stop_btn.clicked.connect(self.stop_video)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_image(self, poster_url):
        session = load_session()
        token = session.get("Authorization", "")
        token = token if not token.startswith("Bearer ") else token
        headers = {"Authorization": token, "User-Agent": "Mozilla/5.0"}

        try:
            request = urllib.request.Request(poster_url, headers=headers)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                image = QtGui.QImage()
                image.loadFromData(data)
                pixmap = QtGui.QPixmap.fromImage(image)
                self.video_label.setPixmap(pixmap.scaled(
                    self.video_label.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                ))
        except Exception as e:
            self.video_label.setText(f"Error al cargar imagen:\n{e}")

    def start_video(self):
        if not self.video_url:
            return

        try:
            # Stop previous video
            self.stop_video()

            self.cap = cv2.VideoCapture(self.video_url)
            if not self.cap.isOpened():
                raise Exception("Could not open video")

            fps = self.cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps > 0 else 33
            self.video_timer.start(delay)

        except Exception as e:
            print(f"[ERROR] start_video: {e}")
            self.video_label.setText(" Error in loading video")

    def pause_video(self):
        self.video_timer.stop()

    def stop_video(self):
        self.video_timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def play_video_frame(self):
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimage = QtGui.QImage(
                frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qimage)
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
        else:
            self.stop_video()


# ---------- SUBCLASSES FOR SPECIALIZED VIEWS ----------

class FreeFootageDetailWidget(ItemDetailWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def load_scene(self, scene_id):
        """Load a scene by its ID and populate the UI.

        Args:
            scene_id (str): The ID of the scene to load.

        """

        session = load_session()
        token = session.get("Authorization", "")
        token = token if token.startswith("Bearer ") else f"Bearer {token}"
        headers = {"User-Agent": "MyApp/1.0", "Authorization": token}

        try:
            # Request the scene with the given ID incluiding header
            url = f"https://backend.actionvfx.com/api/v1/scenes/{scene_id}/"
            print(f"[INFO] Requesting scene: {url}")
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    scene_data = json.loads(response.read().decode("utf-8"))

                    is_pro_user = scene_data.get("free_for_subscriber", False)
                    self.populate_ui_from_scene(scene_data, is_pro_user)
                else:
                    print(f"[ERROR] HTTP status: {response.getcode()}")
        except Exception as e:
            print(f"[ERROR] load_scene: {e}")

    def populate_ui_from_scene(self, scene_data, is_pro_user):
        self.clear_layout(self.thumbnail_layout)
        self.video_path_list = []
        self.button_list = []
        self.variant_combo.clear()
        self.variant_combo.addItem("Select Resolution")

        session = load_session()
        token = session.get("Authorization", "")
        token = token if token.startswith("Bearer ") else f"Bearer {token}"
        headers = {"Authorization": token, "User-Agent": "Mozilla/5.0"}

        clips = scene_data.get("clips", [])

        for i, clip in enumerate(clips):
            name = clip.get("name", f"Clip {i+1}")
            description = scene_data.get("description", "")
            video_url = clip.get("media", {}).get("mp4")
            poster = clip.get("media", {}).get("image") or clip.get("poster")
            thumbnail = clip.get("media", {}).get(
                "image") or scene_data.get("poster")
            variants = clip.get("collection_variants", [])

            if not video_url and not poster:
                print(f"⚠️ Skipping clip {i+1}: No video or poster.")
                continue

            clip_data = {
                "name": name,
                "description": description,
                "poster": poster,
                "video": video_url,
                "thumbnail": thumbnail,
                "variants": variants
            }

    def on_thumbnail_clicked(self, button, item, is_pro_user):
        self.stop_video()
        self.video_url = item.get("video")
        self.name_label.setText(item.get("name", ""))
        self.description_label.setText(item.get("description", ""))

        if self.video_url:
            self.start_video()
        else:
            self.load_image(item.get("poster"))

        # Visual feedback en botones
        for btn in self.button_list:
            btn.setStyleSheet(
                "background-color: #2D2D2D; color: white; text-align: bottom center; font-size: 10px;")
        button.setStyleSheet(
            "background-color: #3ad1ff; color: white; text-align: bottom center; font-size: 10px;")
        self.selected_button = button

        # Load resolutions for the selected clip
        self.variant_combo.clear()
        self.variant_combo.addItem("Select Resolution")

        model = QtGui.QStandardItemModel()
        for var in item.get("variants", []):
            res = var.get("resolution", "??")
            size_bytes = var.get("size", 0)
            size_mb = round(size_bytes / (1024 * 1024))
            size_str = f"{size_mb} MB" if size_bytes > 0 else "?? MB"
            text = f"{res} - {size_str}" + (" 🔒" if not is_pro_user else "")
            item_model = QtGui.QStandardItem(text)
            item_model.setEnabled(is_pro_user)
            model.appendRow(item_model)

        self.variant_combo.setModel(model)


class Collection_DetailWidget(ItemDetailWidget):
    def load_item_by_slug(self, collection_id, item_type="collection_by_id"):
        session = load_session()
        token = session.get("Authorization", "")
        token = token if token.startswith("Bearer ") else f"Bearer {token}"
        headers = {"Authorization": token, "User-Agent": "MyApp/1.0"}

        try:
            url = f"https://backend.actionvfx.com/api/v1/scenes/{collection_id}/"
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    self.populate_ui(data)
        except Exception as e:
            print(f"[ERROR] load 2D collection: {e}")


class OwnershipDetailWidget(ItemDetailWidget):
    def load_item_by_slug(self, collection_id, item_type="collection_by_id"):
        session = load_session()
        token = session.get("Authorization", "")
        token = token if token.startswith("Bearer ") else f"Bearer {token}"
        headers = {"Authorization": token, "User-Agent": "MyApp/1.0"}

        try:
            url = f"https://backend.actionvfx.com/api/v1/collections/{collection_id}/products/"
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    self.populate_ui(data)
        except Exception as e:
            print(f"[ERROR] load Ownership collection: {e}")
