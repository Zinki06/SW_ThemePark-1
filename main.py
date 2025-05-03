import os
import io
import json
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ .env 파일에 GEMINI_API_KEY를 설정하세요.")
    exit(1)

generative_client = genai.Client(api_key=GEMINI_API_KEY)


class DiaryTransformerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("그림일기 체험기")
        self.geometry("1200x800")
        ctk.set_appearance_mode("light")

        # 컬러 팔레트
        PRIMARY = "#017DB3"
        SECONDARY = "#8CD4EA"
        BACKGROUND = "#F9C6C5"  # 전체 배경 연분홍
        PANEL = "#F0FAFC"       # 박스는 하늘빛
        ACCENT = "#F7A6A6"      # 성별 버튼 색상을 부드러운 분홍색으로

        self.configure(fg_color=BACKGROUND)

        # 메인 프레임 (전체 중앙 정렬)
        outer_frame = ctk.CTkFrame(self, fg_color=BACKGROUND)
        outer_frame.pack(expand=True)

        main_frame = ctk.CTkFrame(outer_frame, corner_radius=20, fg_color=BACKGROUND)
        main_frame.grid(row=0, column=0, padx=40, pady=60)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # 왼쪽 입력 영역
        left_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=PANEL)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

        ctk.CTkLabel(left_frame, text="🧸 말하거나 글로 적어서 일기를 그림으로 바꿔보세요!", font=("맑은 고딕", 18, "bold"), text_color="black").pack(pady=20)

        self.input_text = ctk.CTkTextbox(left_frame, height=400, width=700, font=("맑은 고딕", 15, "bold"), corner_radius=10, border_width=1, border_color="#CCCCCC", text_color="black")
        self.input_text.pack(padx=30, pady=15, fill="x")

        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        ctk.CTkButton(button_frame, text="✏️ 일기로 변환", command=self.transform_text, width=160, fg_color=SECONDARY, text_color="black", hover_color=PRIMARY).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="🖼️ 그림 생성", command=self.generate_image, width=160, fg_color=SECONDARY, text_color="black", hover_color=PRIMARY).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="🎙️ 말로 그림 생성", command=self.speech_to_image, width=160, fg_color=SECONDARY, text_color="black", hover_color=PRIMARY).grid(row=0, column=2, padx=10)

        ctk.CTkLabel(left_frame, text="아이 성별 선택:", font=("맑은 고딕", 15, "bold"), text_color="black").pack(pady=(15, 5))
        self.gender_var = ctk.StringVar(value="남자")
        self.gender_menu = ctk.CTkOptionMenu(left_frame, variable=self.gender_var, values=["남자", "여자"], fg_color=ACCENT, text_color="white", button_color=PRIMARY)
        self.gender_menu.pack(pady=(0, 20))

        # 오른쪽 출력 영역
        right_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=PANEL)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)

        ctk.CTkLabel(right_frame, text="📄 변환된 일기 내용:", font=("맑은 고딕", 18, "bold"), text_color="black").pack(pady=(20, 10))
        self.output_text = ctk.CTkTextbox(right_frame, height=400, width=600, font=("맑은 고딕", 13), corner_radius=10, border_width=1, border_color="#CCCCCC", text_color="black")
        self.output_text.pack(padx=30, pady=10, fill="x")
        self.output_text.configure(state="disabled")

        self.image_label = ctk.CTkLabel(right_frame, text="")
        self.image_label.pack(pady=30)

    def transform_text(self):
        original_content = self.input_text.get("1.0", "end").strip()
        if not original_content:
            messagebox.showwarning("⚠️ 경고", "원본 내용을 입력하세요.")
            return
        try:
            transformed_content = self.call_gemini_for_diary(original_content)
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", transformed_content)
            self.output_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("오류", f"텍스트 변환 중 오류 발생: {e}")

    def call_gemini_for_diary(self, text: str) -> str:
        prompt = f'다음 텍스트를 5세에서 13세 사이의 아이가 그림일기에 쓸 법한 3~5 문장의 짧은 글로 바꿔줘. 친근하고 쉬운 단어를 사용해줘. 기존 내용에 충실하도록 해줘:\n\n"{text}"'
        response = generative_client.models.generate_content(
            model="models/gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=genai_types.GenerateContentConfig(response_modalities=["TEXT"])
        )
        if response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        elif hasattr(response, 'text'):
            return response.text
        else:
            raise Exception("Gemini API로부터 텍스트를 추출할 수 없습니다.")

    def call_gemini_generate(self, text: str):
        gender = self.gender_var.get()
        combined_prompt = (
            f"다음 문장을 바탕으로 지브리 애니메이션 스타일의 일러스트를 그려줘. "
            f"문장: \"{text}\"\n\n"
            f"그림에는 반드시 {gender} 아이가 등장해야 하고, 문장의 내용이 그림으로 잘 전달되어야 해. "
            f"배경은 몽환적이고 동화 같은 느낌으로, 부드러운 색감과 따뜻한 분위기로 그려줘. "
            f"글자는 포함하지 말고, 인물은 반드시 1명만 있어야 해."
        )
        response = generative_client.models.generate_content(
            model="models/gemini-2.0-flash-exp-image-generation",
            contents=combined_prompt,
            config=genai_types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
        )
        text_output = ""
        image = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_output += part.text
            elif part.inline_data is not None:
                image = Image.open(io.BytesIO(part.inline_data.data))
        return text_output, image

    def show_image(self, pil_img):
        img = pil_img.copy()
        img.thumbnail((400, 400))
        tk_img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=tk_img)
        self.image_label.image = tk_img

    def generate_image(self):
        original_content = self.input_text.get("1.0", "end").strip()
        if not original_content:
            messagebox.showwarning("⚠️ 경고", "원본 내용을 입력하세요.")
            return
        try:
            text, image = self.call_gemini_generate(original_content)
            if image:
                self.show_image(image)
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", text)
            self.output_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("오류", f"그림 생성 중 오류 발생: {e}")

    def speech_to_image(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            messagebox.showinfo("🎙️ 말하기 시작", "이제 말을 시작하세요. 멈추면 자동으로 인식합니다.")
            audio = recognizer.listen(source)
        try:
            spoken_text = recognizer.recognize_google(audio, language="ko-KR")
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", spoken_text)
            self.generate_image()
        except sr.UnknownValueError:
            messagebox.showerror("오류", "음성을 인식할 수 없습니다.")
        except sr.RequestError as e:
            messagebox.showerror("오류", f"STT 요청 중 오류 발생: {e}")


if __name__ == "__main__":
    if not GEMINI_API_KEY or not GEMINI_API_KEY.startswith("AIza"):
        print("❌ .env 파일에서 유효한 GEMINI_API_KEY를 설정하세요.")
    else:
        app = DiaryTransformerApp()
        app.mainloop()
