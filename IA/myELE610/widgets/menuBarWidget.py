from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow



def MenuBar(self: QMainWindow):
    menu_bar = self.menuBar()
    file_menu = menu_bar.addMenu("File")
    info_menu = menu_bar.addMenu("Image")

    open_action = QAction("Open", self)
    open_action.triggered.connect(self.open_image)

    exit_action = QAction("Exit", self)
    exit_action.triggered.connect(self.close)

    print_action = QAction("Print Info", self)
    print_action.triggered.connect(self.print_image_info)

    reset_action = QAction("Reset", self)
    reset_action.triggered.connect(self.reset)

    grayscale_action = QAction("Show Grayscale", self)
    grayscale_action.triggered.connect(self.convert_to_grayscale)

    edge_action = QAction("Sobel Edges", self)
    edge_action.triggered.connect(self.convert_to_edges)

    binary_action = QAction("Convert to Binary", self)
    binary_action.triggered.connect(self.convert_to_binary)

    hough_action = QAction("Show Hough Lines", self)
    hough_action.triggered.connect(self.show_hough_lines)

    file_menu.addAction(open_action)
    file_menu.addAction(exit_action)

    info_menu.addAction(print_action)
    info_menu.addAction(grayscale_action)
    info_menu.addAction(edge_action)
    info_menu.addAction(binary_action)
    info_menu.addAction(hough_action)
    info_menu.addAction(reset_action)

if __name__ == '__main__':
    pass