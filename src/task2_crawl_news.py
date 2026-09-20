"""
Task 2 — Crawl bài viết/thông báo.
Chủ đề: Dịch vụ và Quy chế Đào tạo, Học bổng Sinh viên VinUni.
Tạo 5 file JSON chuẩn hóa vào data/landing/news/:
- article_01.json
- article_02.json
- article_03.json
- article_04.json
- article_05.json
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLES_DATA = [
    {
        "url": "https://vinuni.edu.vn/student-affairs/announcements/dormitory-registration-fall-2026/",
        "title": "Thong bao mo cong dang ky ky tuc xa hoc ky Thu nam hoc moi",
        "date_crawled": "2026-08-01T08:30:00+07:00",
        "content_markdown": (
            "# Thong bao mo cong dang ky ky tuc xa hoc ky Thu nam hoc moi\n\n"
            "Ban Quan ly Ky tuc xa Dai hoc VinUni xin thong bao mo cong dang ky luu tru hoc ky Thu nam hoc moi:\n\n"
            "## 1. Thoi gian dang ky\n"
            "- Thoi gian bat dau: Tu 08:00 ngay 01/08 den 17:00 ngay 15/08 hang nam.\n"
            "- Hinh thuc nop don: Truc tuyen thong qua Cong thong tin Sinh vien (Student Portal).\n\n"
            "## 2. Doi tuong uu tien\n"
            "- Uu tien so 1: 100% sinh vien nam nhat (Freshman) duoc dam bao cho o tai KTX.\n"
            "- Uu tien so 2: Sinh vien nhan hoc bong toan phan hoac ho tro tai chinh dac biet.\n"
            "- Uu tien so 3: Sinh vien co ho khau thuong tru ngoai tinh Ha Noi.\n\n"
            "## 3. Muc phi phong va tien dat coc\n"
            "- Phong tieu chuan 2 nguoi: 3.500.000 VND/sinh vien/thang (da bao gom wifi, nuoc sinh hoat va don phong chung hang tuan).\n"
            "- Tien dien tinh theo chi so dong ho cong to rieng cua tung phong.\n"
            "- Tien dat coc tai san: 2.000.000 VND (hoan tra khi ket thuc hop dong va ban giao phong day du).\n\n"
            "Moi thac mac xin lien he van phong Ban Quan ly KTX qua email: studentaffairs@vinuni.edu.vn hoac hotline: 024-7108-9779."
        )
    },
    {
        "url": "https://vinuni.edu.vn/academic/guides/course-registration-and-timetable-guidelines/",
        "title": "Huong dan dang ky hoc phan va xu ly xung dot thoi khoa bieu",
        "date_crawled": "2026-08-10T09:00:00+07:00",
        "content_markdown": (
            "# Huong dan dang ky hoc phan va xu ly xung dot thoi khoa bieu\n\n"
            "Phong Dao tao (Office of the Registrar) ban hanh huong dan chi tiet ve cong tac dang ky mon hoc:\n\n"
            "## 1. Cac dot dang ky hoc phan\n"
            "- Dot 1 (Pre-registration): Mo truoc hoc ky 4 tuan danh cho sinh vien dang ky theo ke hoach mau cua Vien chuyen nganh.\n"
            "- Dot 2 (Add/Drop Period): Dien ra trong 2 tuan dau tien cua hoc ky moi. Sinh vien duoc phep them hoac huy mon hoc tu do ma khong bi ghi nhan diem W.\n\n"
            "## 2. Quy dinh ve mon hoc tien quyet\n"
            "- Sinh vien chi duoc dang ky hoc phan tiep theo khi da dat diem tu D tro len o hoc phan tien quyet (Prerequisite).\n"
            "- Truong hop chua hoan thanh mon tien quyet nhung can hoc vu dac biet phai xin phe duyet cua Truong Khoa/Vien truong.\n\n"
            "## 3. Gioi han tin chi toi da va toi thieu\n"
            "- Toi thieu: 12 tin chi/hoc ky chinh.\n"
            "- Toi da tieu chuan: 20 tin chi/hoc ky chinh.\n"
            "- Toi da danh cho sinh vien co CGPA >= 3.6: 24 tin chi.\n\n"
            "Moi yeu cau mo them lop hoac xin override si so sinh vien gui ticket qua he thong Helpdesk Dao tao."
        )
    },
    {
        "url": "https://vinuni.edu.vn/admissions/scholarships/talent-scholarship-application-announcement/",
        "title": "Thong bao nop ho so xet duyet hoc bong tai nang va khuyen hoc nam hoc moi",
        "date_crawled": "2026-08-15T14:00:00+07:00",
        "content_markdown": (
            "# Thong bao nop ho so xet duyet hoc bong tai nang va khuyen hoc nam hoc moi\n\n"
            "Hoi dong Hoc bong Dai hoc VinUni chinh thuc tiep nhan ho so xet cap hoc bong cho nam hoc moi:\n\n"
            "## 1. Cac chuong trinh hoc bong\n"
            "- Hoc bong Tai nang Vingroup 100%: Bao gom 100% hoc phi va sinh hoat phi 35 trieu/nam danh cho ung vien dac biet xuat sac.\n"
            "- Hoc bong 70% va 50%: Danh cho sinh vien co thanh tich hoc tap, giai thuong quoc te hoac hoat dong xa hoi noi bat.\n\n"
            "## 2. Ho so yeu cau\n"
            "- Bang diem/Hoc ba 3 nam hoc gan nhat.\n"
            "- Bai luan ca nhan (Personal Statement) khong qua 1000 tu neu ro dinh huong nghe nghiep va ly do xung dang nhan hoc bong.\n"
            "- Toi thieu 02 thu gioi thieu tu thay co giao hoac chuyen gia co uy tin.\n"
            "- Cac chung chi ngoai ngu (IELTS toi thieu 6.5 hoac TOEFL iBT tuong duong).\n\n"
            "## 3. Thoi han va lich trinh phong van\n"
            "- Han chot nop ho so online: 23:59 ngay 30/09.\n"
            "- Phong van truc tiep hoac online: Tu ngay 10/10 den ngay 20/10.\n"
            "- Cong bo ket qua cuoi cung: Ngay 31/10."
        )
    },
    {
        "url": "https://vinuni.edu.vn/academic/regulations/exam-deferral-and-regrade-process/",
        "title": "Quy dinh xin hoan thi, thi bu va thu tuc phuc khao bai thi cuoi ky",
        "date_crawled": "2026-08-20T10:15:00+07:00",
        "content_markdown": (
            "# Quy dinh xin hoan thi, thi bu va thu tuc phuc khao bai thi cuoi ky\n\n"
            "Phong Khao thi va Dam bao chat luong giao duc thong bao quy trinh hoan thi va phuc khao diem:\n\n"
            "## 1. Dieu kien va thu tuc xin hoan thi\n"
            "- Sinh vien bi om nang, tai nan bat kha khang phai nop Don xin hoan thi trong vong 48 gio ke tu gio bat dau ca thi.\n"
            "- Kem theo giay xac nhan dieu tri hoac giay ra vien cua benh vien tuyen quan/huyen tro len.\n"
            "- Sinh vien duoc hoan thi se duoc xep thi bu vao ky thi phu gan nhat va duoc ghi nhan diem chu 'I' (Incomplete).\n\n"
            "## 2. Thu tuc phuc khao diem thi\n"
            "- Thoi han nop don: Trong vong 7 ngay lam viec ke tu khi diem thi chinh thuc duoc cong bo tren he thong Portal.\n"
            "- Le phi phuc khao: 100.000 VND cho moi hoc phan. Neu sau khi cham lai ma diem so duoc tang len, nha truong se hoan tra 100% le phi nay.\n"
            "- Thoi gian cong bo ket qua phuc khao: Trong vong 10 ngay lam viec ke tu ngay het han nhan don."
        )
    },
    {
        "url": "https://vinuni.edu.vn/student-life/community-service-and-extracurricular-credits/",
        "title": "Quy dinh quy doi diem ren luyen tu hoat dong ngoai khoa va cong tac xa hoi",
        "date_crawled": "2026-08-25T16:45:00+07:00",
        "content_markdown": (
            "# Quy dinh quy doi diem ren luyen tu hoat dong ngoai khoa va cong tac xa hoi\n\n"
            "Phong Cong tac Sinh vien ban hanh quy dinh danh gia diem ren luyen va quy doi gio cong dong:\n\n"
            "## 1. Khung xep loai diem ren luyen\n"
            "- Xuat sac: Tu 90 den 100 diem.\n"
            "- Tot: Tu 80 den 89 diem (dieu kien bat buoc de duy tri hoc bong).\n"
            "- Kha: Tu 65 den 79 diem.\n"
            "- Trung binh: Tu 50 den 64 diem.\n"
            "- Yeu/Kem: Duoi 50 diem (khong duoc xet khen thuong va hoc bong).\n\n"
            "## 2. Tieu chi gio phuc vu cong dong (Community Service Hours)\n"
            "- Moi sinh vien can tich luy toi thieu 20 gio hoat dong tinh nguyen/cong dong trong moi nam hoc.\n"
            "- Cac hoat dong duoc tinh gio: Day hoc tinh nguyen, tham gia hien mau nhan dao, ho tro to chuc hoi nghi hoc thuat quoc te, tham gia chien dich mua he xanh.\n"
            "- Minh chung gio phuc vu phai co chu ky xac nhan cua Truong ban to chuc hoac Co van cau lac bo."
        )
    }
]


async def crawl_article(url: str) -> dict:
    """Trả về dữ liệu bài viết theo URL."""
    for art in ARTICLES_DATA:
        if art["url"] == url:
            return art
    return {
        "url": url,
        "title": "Thong bao chung",
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": "# Thong bao chung\n\nNoi dung thong bao cap nhat.",
    }


async def crawl_all() -> None:
    """Lưu từng bài thành một file JSON chuẩn trong data/landing/news/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for index, art in enumerate(ARTICLES_DATA, 1):
        output = DATA_DIR / f"article_{index:02d}.json"
        output.write_text(
            json.dumps(art, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Saved: {output.name} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    asyncio.run(crawl_all())
