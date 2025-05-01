import os
import io
import tkinter as tk
from dotenv import load_dotenv
from tkinter import messagebox, scrolledtext
from google import genai
from google.genai import types as genai_types
from PIL import Image, ImageTk

# Load environment variables from .env
load_dotenv()

# Read Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ .env 파일에 GEMINI_API_KEY를 설정하세요.")
    exit(1)

# Initialize Gemini client
generative_client = genai.Client(api_key=GEMINI_API_KEY)

class DiaryTransformerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("그림일기 내용 변환기")
        self.geometry("600x500")

        tk.Label(self, text="원본 내용을 입력하세요:").pack(pady=(10, 0))
        self.input_text = scrolledtext.ScrolledText(self, height=10, width=70, wrap=tk.WORD)
        self.input_text.pack(pady=5)

        tk.Button(self, text="일기 내용으로 변환", command=self.transform_text).pack(pady=10)

        # Gender selection
        tk.Label(self, text="아이 성별 선택:").pack(pady=(10, 0))
        self.gender_var = tk.StringVar(self)
        self.gender_var.set("남자")  # 기본값
        tk.OptionMenu(self, self.gender_var, "남자", "여자").pack(pady=5)

        # Generate image button
        tk.Button(self, text="그림 생성", command=self.generate_image).pack(pady=10)

        # Image display label
        self.image_label = tk.Label(self)
        self.image_label.pack(pady=5)

        tk.Label(self, text="변환된 내용:").pack(pady=(10, 0))
        self.output_text = scrolledtext.ScrolledText(self, height=10, width=70, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(pady=5)

    def transform_text(self):
        original_content = self.input_text.get("1.0", tk.END).strip()
        if not original_content:
            messagebox.showwarning("경고", "원본 내용을 입력하세요.")
            return

        try:
            transformed_content = self.call_gemini_for_diary(original_content)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, transformed_content)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("오류", f"텍스트 변환 중 오류 발생: {e}")

    def call_gemini_for_diary(self, text: str) -> str:
        # 모델 이름 변경 (텍스트 생성에 적합한 모델로)
        # model = generative_client.get_generative_model('gemini-pro') # get_generative_model 제거
        # f-string 외부를 싱글 쿼트로 변경하여 내부 더블 쿼트 문제 해결
        prompt = f'다음 텍스트를 5세에서 13세 사이의 아이가 그림일기에 쓸 법한 3~5 문장의 짧은 글로 바꿔줘. 친근하고 쉬운 단어를 사용해줘. 기존 내용에 충실하도록 해줘:\n\n"{text}"'

        # generate_content 직접 호출
        response = generative_client.models.generate_content(
            model="models/gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["TEXT"]
            )
        )

        # 응답 구조 확인 및 텍스트 추출 (오류 처리 추가)
        try:
            # response.text 직접 접근 시도 (Gemini API 변경 가능성 고려)
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            elif hasattr(response, 'text'): # 이전 방식 호환성
                return response.text
            else:
                # 예상치 못한 응답 구조 처리
                print("Unexpected response structure:", response)
                raise Exception("Gemini API로부터 텍스트를 추출할 수 없습니다.")
        except (AttributeError, IndexError, KeyError, StopIteration) as e:
             # 다양한 오류 상황 처리
            print(f"Error extracting text from response: {e}")
            print("Full response:", response) # 디버깅 위해 전체 응답 출력
            raise Exception(f"Gemini API 응답 처리 중 오류 발생: {e}")

    def show_image(self, pil_img):
        # Display PIL image in the GUI
        img = pil_img.copy()
        img.thumbnail((400, 400))
        tk_img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=tk_img)
        self.image_label.image = tk_img

    def call_gemini_generate(self, text: str):
        # Build instruction prompt including selected gender
        gender = self.gender_var.get()
        sys_prompt = f"다음 내용에 맞게 아이들이 좋아하도록 동심 가득하게 지브리 스타일로 그려줘. 글은 쓰지마. {gender} 아이 한 명을 무조건 그려줘"
        combined_prompt = f"{sys_prompt}: {text}"
        response = generative_client.models.generate_content(
            model="models/gemini-2.0-flash-exp-image-generation",
            contents=combined_prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        text_output = ""
        image = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_output += part.text
            elif part.inline_data is not None:
                image = Image.open(io.BytesIO(part.inline_data.data))
        return text_output, image

    def generate_image(self):
        original_content = self.input_text.get("1.0", tk.END).strip()
        if not original_content:
            messagebox.showwarning("경고", "원본 내용을 입력하세요.")
            return
        try:
            text, image = self.call_gemini_generate(original_content)
            # Show generated image
            if image:
                self.show_image(image)
            # Show generated text
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, text)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("오류", f"그림 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    if not GEMINI_API_KEY or not GEMINI_API_KEY.startswith("AIza"):
        print("❌ .env 파일에서 유효한 GEMINI_API_KEY를 설정하세요.")
    else:
        app = DiaryTransformerApp()
        app.mainloop()
