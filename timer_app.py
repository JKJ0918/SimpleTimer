import pygame
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import StringVar
from PIL import Image, ImageDraw, ImageTk
import threading
import time
import math
from tkinter import messagebox


class SVGLikeTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("원형 타이머")
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.total_time = 0

        self.size = 200  # Canvas / Image 크기
        self.time_str = StringVar(value="00:00")

        self.style = ttk.Style("cyborg")

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        self.canvas = tk.Canvas(frame, width=self.size, height=self.size, bg="#222", highlightthickness=0)
        self.canvas.pack()

        self.canvas_img = self.canvas.create_image(0, 0, anchor="nw")

        self.canvas_text = self.canvas.create_text(
            self.size // 2, self.size // 2,
            text=self.time_str.get(),
            font=("Helvetica", 18),
            fill="white"
        )

        # 시간 입력
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10)

        self.hours = ttk.Entry(input_frame, width=5, justify="center")
        self.hours.insert(0, "00")
        self.hours.pack(side="left", padx=5)
        ttk.Label(input_frame, text="시").pack(side="left")

        self.minutes = ttk.Entry(input_frame, width=5, justify="center")
        self.minutes.insert(0, "00")
        self.minutes.pack(side="left", padx=5)
        ttk.Label(input_frame, text="분").pack(side="left")

        self.seconds = ttk.Entry(input_frame, width=5, justify="center")
        self.seconds.insert(0, "00")
        self.seconds.pack(side="left", padx=5)
        ttk.Label(input_frame, text="초").pack(side="left")

        # 버튼
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="시작", command=self.start_timer, bootstyle="OUTLINE").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="정지", command=self.pause_timer, bootstyle="OUTLINE").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="계속", command=self.resume_timer, bootstyle="OUTLINE").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="초기화", command=self.reset_timer, bootstyle="WARNING-OUTLINE").pack(side="left", padx=5)

    def start_timer(self):
        if not self.running:
            try:
                hrs = int(self.hours.get())
                mins = int(self.minutes.get())
                secs = int(self.seconds.get())
                self.total_time = hrs * 3600 + mins * 60 + secs
                self.remaining_time = self.total_time
                self.running = True
                self.paused = False
                threading.Thread(target=self.countdown, daemon=True).start()
            except ValueError:
                self.update_text("입력 오류")

    def pause_timer(self):
        self.paused = True

    def resume_timer(self):
        if self.running and self.paused:
            self.paused = False
            threading.Thread(target=self.countdown, daemon=True).start()

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.update_text("00:00")
        self.draw_arc(0)

    def countdown(self):
        while self.remaining_time > 0 and self.running:
            if not self.paused:
                self.update_display()
                time.sleep(1)
                self.remaining_time -= 1
        if self.remaining_time <= 0 and self.running:
            self.update_display()
            self.running = False
            self.play_alarm() # 알람 소리
            self.show_popup() # 팝업 메시지

    def play_alarm(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("alarm.wav")
            pygame.mixer.music.play()
        except Exception as e:
            print("알림 소리 재생 실패:", e)

    def show_popup(self):
        messagebox.showinfo("타이머 종료", "⏰ 시간이 완료되었습니다!")

    def update_display(self):
        hrs, rem = divmod(self.remaining_time, 3600)
        mins, secs = divmod(rem, 60)
        self.update_text(f"{hrs:02d}:{mins:02d}:{secs:02d}")
        percent = (self.total_time - self.remaining_time) / self.total_time if self.total_time else 0
        self.draw_arc(percent)

    def update_text(self, text):
        self.time_str.set(text)
        self.canvas.itemconfig(self.canvas_text, text=text)

    def draw_arc(self, percent):
        img = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 배경 원형 (밝은 회색)
        draw.arc([10, 10, self.size - 10, self.size - 10], 0, 360, fill=(80, 80, 80, 80), width=14)

        start_angle = -90
        end_angle = start_angle + (percent * 360)

        # 그라디언트 색상 범위: 파랑 → 시안 → 민트
        def get_gradient_color(angle_percent):
            # angle_percent: 0.0 ~ 1.0
            if angle_percent < 0.5:
                # 빨강 → 핑크 (#FF3C3C → #FF70C0)
                p = angle_percent / 0.5
                r = 255
                g = int(60 + (112 - 60) * p)  # 60 → 112
                b = int(60 + (192 - 60) * p)  # 60 → 192
            else:
                # 핑크 → 노랑 (#FF70C0 → #FFD93C)
                p = (angle_percent - 0.5) / 0.5
                r = 255
                g = int(112 + (217 - 112) * p)  # 112 → 217
                b = int(192 - (192 - 60) * p)  # 192 → 60

            return (r, g, b, 255)

        # 세그먼트 분할로 아크 그리기 (1도 단위로)
        segments = 200
        segment_angle = (end_angle - start_angle) / segments

        for i in range(segments):
            ang1 = start_angle + i * segment_angle
            ang2 = ang1 + segment_angle
            color = get_gradient_color(i / segments)
            draw.arc([10, 10, self.size - 10, self.size - 10], ang1, ang2, fill=color, width=14)

        tk_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.canvas_img, image=tk_image)
        self.canvas.image = tk_image


if __name__ == "__main__":
    root = ttk.Window(themename="cyborg", size=(300, 400))
    app = SVGLikeTimer(root)
    root.mainloop()







