import tkinter as tk
from tkinter import filedialog, messagebox
import os
import cv2 as cv
from PIL import Image


class VideoToPDFApp:
    def __init__(self, root):
        # окно
        self.root = root
        self.root.title("Video to PDF")
        self.root.configure(bg="#444444")  # фон

        # ---------- ПУТЬ К ВИДЕО ----------
        self.path_label = tk.Label(root, text="Путь к видео:", bg="#444444", fg="white")
        self.path_label.pack()

        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack()

        self.browse_btn = tk.Button(root, text="Выбрать файл", command=self.browse_file)
        self.browse_btn.pack()

        # ---------- ПАПКА СОХРАНЕНИЯ ----------
        self.save_label = tk.Label(root, text="Папка сохранения:", bg="#444444", fg="white")
        self.save_label.pack()

        self.save_entry = tk.Entry(root, width=50)
        self.save_entry.pack()

        self.save_btn = tk.Button(root, text="Выбрать папку", command=self.browse_folder)
        self.save_btn.pack()

        # ---------- КООРДИНАТЫ ----------
        self.coord_label = tk.Label(root, text="Координаты:", bg="#444444", fg="white")
        self.coord_label.pack()

        coord_frame = tk.Frame(root, bg="#444444")
        coord_frame.pack()

        self.x1_entry = tk.Entry(coord_frame, width=5)
        self.x1_entry.grid(row=0, column=0, padx=5)
        tk.Label(coord_frame, text="x1", bg="#444444", fg="white").grid(row=1, column=0)

        self.y1_entry = tk.Entry(coord_frame, width=5)
        self.y1_entry.grid(row=0, column=1, padx=5)
        tk.Label(coord_frame, text="y1", bg="#444444", fg="white").grid(row=1, column=1)

        self.x2_entry = tk.Entry(coord_frame, width=5)
        self.x2_entry.grid(row=0, column=2, padx=5)
        tk.Label(coord_frame, text="x2", bg="#444444", fg="white").grid(row=1, column=2)

        self.y2_entry = tk.Entry(coord_frame, width=5)
        self.y2_entry.grid(row=0, column=3, padx=5)
        tk.Label(coord_frame, text="y2", bg="#444444", fg="white").grid(row=1, column=3)

        
        # ---------- ИНТЕРВАЛ ----------
        self.interval_label = tk.Label(root, text="Интервал (сек):", bg="#444444", fg="white")
        self.interval_label.pack()

        self.interval_entry = tk.Entry(root)
        self.interval_entry.pack()

        # ---------- КНОПКИ ----------
        self.start_btn = tk.Button(root, text="Запуск", command=self.start_processing)
        self.start_btn.pack(pady=10)

        self.exit_btn = tk.Button(root, text="Выход", command=root.quit)
        self.exit_btn.pack()

    def browse_file(self):
        # выбор файла
        file_path = filedialog.askopenfilename()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, file_path)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(0, folder_path)

    def start_processing(self):
        try:
            path = self.path_entry.get()
            save_path = self.save_entry.get()
            # координаты
            x1 = int(self.x1_entry.get())
            y1 = int(self.y1_entry.get())
            x2 = int(self.x2_entry.get())
            y2 = int(self.y2_entry.get())

            # интервал
            interval_sec = float(self.interval_entry.get())

            # запуск
            processor = VideoProcessor(path, (x1, y1, x2, y2), interval_sec, save_path)
            processor.process_video()
            
            messagebox.showinfo("Готово", "PDF успешно создан!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class VideoProcessor:
    def __init__(self, path, coords, interval_sec, save_path):
        self.path = path
        self.x1, self.y1, self.x2, self.y2 = coords
        self.interval_sec = interval_sec
        self.save_path = save_path

        self.images = []

    def process_video(self):
        # видео
        cap = cv.VideoCapture(self.path)

        if not cap.isOpened():
            raise ValueError("Не удалось открыть видео")

        # слайды
        fps = cap.get(cv.CAP_PROP_FPS)

        # шаг в кадрах
        frame_interval = int(fps * self.interval_sec)

        frame_count = 0

        # первый кадр
        ok, frame = cap.read()
        if not ok:
            raise ValueError("Ошибка чтения видео")

        h, w = frame.shape[:2]

        # проверка координат
        if not (0 <= self.x1 < self.x2 <= w and 0 <= self.y1 < self.y2 <= h):
            raise ValueError("Неверные координаты области")

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # проверка интервала
            if frame_count % frame_interval == 0:
                # вырезание области
                crop = frame[self.y1:self.y2, self.x1:self.x2]

                # конвертация
                img = Image.fromarray(cv.cvtColor(crop, cv.COLOR_BGR2RGB))
                self.images.append(img)

            frame_count += 1

        cap.release()

        # сохранение PDF
        if self.images:
            output_file = os.path.join(self.save_path, "slides.pdf")

            self.images[0].save(
            output_file,
            save_all=True,
            append_images=self.images[1:])
            
        else:
            raise ValueError("Нет сохранённых кадров")

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToPDFApp(root)
    root.mainloop()