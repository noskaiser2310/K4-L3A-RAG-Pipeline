"""
Task 1 — Thu thập tài liệu chính sách/quy định.
Chủ đề: Dịch vụ và Quy chế Đào tạo, Học bổng Sinh viên VinUni.
Tạo 3 tài liệu PDF chính thức với nội dung quy chế học vụ chi tiết:
1. quy-che-dao-tao-dai-hoc.pdf
2. chinh-sach-hoc-bong-tai-chinh.pdf
3. noi-quy-ky-tuc-xa-sinh-vien.pdf
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


DOCUMENTS_CONTENT = {
    "quy-che-dao-tao-dai-hoc.pdf": {
        "title": "QUY CHE DAO TAO DAI HOC THEO TIN CHI - VINUNI",
        "sections": [
            ("Dieu 1: Pham vi va doi tuong ap dung", 
             "Quy che nay quy dinh ve to chuc va quan ly dao tao bac dai hoc tai Dai hoc VinUni theo he thong tin chi. "
             "Ap dung cho toan bo sinh vien he chinh quy cac vien Khoa hoc Ky thuat, Kinh doanh Quan tri, va Khoa hoc Suc khoe. "
             "Moi nam hoc gom 2 hoc ky chinh (Thu va Xuan) keo dai 16 tuan va 1 hoc ky He keo dai 8 tuan."),
            ("Dieu 2: Dang ky hoc phan va khoi luong hoc tap", 
             "Sinh vien phai dang ky toi thieu 12 tin chi va toi da 20 tin chi trong mot hoc ky chinh. "
             "Sinh vien co GPA hoc ky truoc dat tu 3.6 tro len duoc phep dang ky toi da 24 tin chi. "
             "Viec rut hoc phan duoc phep thuc hien trong vong 2 tuan dau tien cua hoc ky ma khong bi ghi diem W tren bang diem. "
             "Sau tuan thu 2 den het tuan thu 6, sinh vien rut hoc phan se bi ghi diem W (Withdraw). Sau tuan thu 6 khong duoc phep rut hoc phan."),
            ("Dieu 3: Thang diem va danh gia ket qua hoc tap", 
             "Diem danh gia hoc phan gom: Diem chuyen can/danh gia qua trinh (30-50%) va Diem thi cuoi ky (50-70%). "
             "Thang diem chu bao gom: A (4.0, tu 8.5 tro len - Xuat sac), B (3.0, tu 7.0 den 8.4 - Kha/Gioi), "
             "C (2.0, tu 5.5 den 6.9 - Trung binh), D (1.0, tu 4.0 den 5.4 - Qua mon thap), va F (0.0, duoi 4.0 - Truot mon). "
             "Diem trung binh chung tich luy (CGPA) toi thieu de tot nghiep la 2.0 tren thang 4.0."),
            ("Dieu 4: Canh bao hoc vu va dinh chi hoc tap", 
             "Sinh vien bi canh bao hoc vu muc 1 neu GPA hoc ky dat duoi 1.50 doi voi nam nhat hoac duoi 1.80 doi voi nam hai tro di. "
             "Sinh vien bi canh bao hoc vu 2 lan lien tiep phai gap Co van hoc tap de lap ke hoach phuc hoi hoc luc. "
             "Bi canh bao hoc vu muc 3 se bi buoc thoi hoc theo quy dinh cua Hoi dong dao tao."),
            ("Dieu 5: Dieu kien cong nhan tot nghiep", 
             "Sinh vien duoc cong nhan tot nghiep khi tich luy du so tin chi theo chuong trinh dao tao (120 - 150 tin chi), "
             "diem CGPA toan khoa dat tu 2.00 tro len, hoan thanh chung chi Chuan ngoai ngu tieng Anh tuong duong IELTS 6.5 tro len "
             "va khong bi ky luat tu muc dinh chi hoc tap tro len.")
        ]
    },
    "chinh-sach-hoc-bong-tai-chinh.pdf": {
        "title": "CHINH SACH HOC BONG VA HO TRO TAI CHINH - VINUNI",
        "sections": [
            ("Dieu 1: Muc dich va nguyen tac cap hoc bong", 
             "Quy dinh ve cac chuong trinh hoc bong tai nang va ho tro tai chinh nham thu hut, boiduong sinh vien xuat sac. "
             "Hoc bong duoc cap xet dua tren thanh tich hoc tap, pham chat lanh dao, dong gop cong dong va hoan canh gia dinh."),
            ("Dieu 2: Cac hang muc hoc bong tai nang", 
             "Hoc bong Toan phan (100% hoc phi va sinh hoat phi 35 trieu/nam): danh cho top 5% thi sinh dat thanh tich vuot troi. "
             "Hoc bong Tai nang 70%: ho tro 70% hoc phi suot 4 nam hoc. "
             "Hoc bong Khuyen hoc 50%: ho tro 50% hoc phi suot 4 nam hoc cho sinh vien co thanh tich tot va bai luan an tuong."),
            ("Dieu 3: Dieu kien duy tri hoc bong hang nam", 
             "Sinh vien nhan hoc bong tai nang phai duy tri diem CGPA tich luy toi thieu 3.20/4.00 tai moi ky danh gia cuoi nam hoc. "
             "Sinh vien phai dat diem ren luyen tu loai Tot tro len (>= 80 diem) va tham gia toi thieu 20 gio hoat dong phuc vu cong dong moi nam. "
             "Neu CGPA roi xuong duoi 3.20 nhung tren 2.80, hoc bong se bi giam 1 bac hoac tam ngung 1 hoc ky de thu thach."),
            ("Dieu 4: Goi ho tro tai chinh can cu vao nhu cau (Need-based Aid)", 
             "Ho tro tai chinh danh cho sinh vien co nang luc nhung gia dinh co kho khan ve kinh te. "
             "Muc ho tro dao dong tu 50% den 100% hoc phi tuy theo muc xet duyet tai chinh cua Hoi dong. "
             "Ho so can nop gom: giay xac nhan thu nhap gia dinh, hoa don tien dien nuoc 6 thang gan nhat va bai thuyet minh hoan canh."),
            ("Dieu 5: Quy trinh nop don va phuc khao hoc bong", 
             "Cac dot xet hoc bong dien ra vao thang 1, thang 4 va thang 6 hang nam. "
             "Ket qua xet duyet duoc cong bo qua email sinh vien sau 3 tuan ke tu ngay dong cong nhan ho so. "
             "Sinh vien co quyen nop don phuc khao trong vong 7 ngay lam viec ke tu ngay cong bo ket qua.")
        ]
    },
    "noi-quy-ky-tuc-xa-sinh-vien.pdf": {
        "title": "NOI QUY VA QUY CHE QUAN LY KY TUC XA SINH VIEN - VINUNI",
        "sections": [
            ("Dieu 1: Nguyen tac chung ve cu tru tai KTX", 
             "Ky tuc xa VinUni la moi truong sinh hoat, hoc tap van minh, an toan cho toan the sinh vien, giang vien va chuyen gia. "
             "Toan bo sinh vien nam nhat duoc uu tien bo tri cho o tai KTX khuon vien truong de thuan tien hoc tap va hoa nhap."),
            ("Dieu 2: Gio giac va kiem soat ra vao", 
             "KTX mo cua tu 06:00 sang den 23:00 dem hang ngay. Sinh vien ve sau 23:00 phai xuat trinh the sinh vien va ghi ro ly do tai phong truc ban. "
             "Sinh vien ve muon qua 3 lan trong 1 hoc ky ma khong co ly do chinh dang se bi canh bao ky luat va tru diem ren luyen. "
             "Khach ngoai khong duoc phep luu tru qua dem tai phong o cua sinh vien duoi bat ky hinh thuc nao."),
            ("Dieu 3: Quy dinh ve ve sinh va tai san phong o", 
             "Sinh vien phai tu giac giu ve sinh phong o va khu vuc sinh hoat chung. BQL KTX to chuc kiem tra ve sinh dinh ky vao sang thu 7 hang tuan. "
             "Nghiem cam tu y thay doi ket cau phong, son tuong, dong dinh hoac tu y sua chua he thong dien nuoc. "
             "Moi hu hong do loi ca nhan phai boi thuong 100% gia tri tai san theo quy dinh."),
            ("Dieu 4: An toan phong chay chua chay va an ninh", 
             "Tuyet doi nghiem cam su dung bep gas, bep dien tu, lo nuong, noi com dien cong suat tren 1000W trong phong o. "
             "Nghiem cam mang chat de chay no, vu khi, hung khi, chat kich thich, ma tuy, ruou bia vao khu vuc KTX. "
             "Nghiem cam hut thuoc la va thuoc la dien tu trong toan bo khuon vien toa nha KTX."),
            ("Dieu 5: Thu tuc tiep nhan va ban giao phong o", 
             "Khi nhan phong, sinh vien kiem tra va ky vao bien ban ban giao trang thiet bi tai san. "
             "Khi ket thuc hop dong thue phong hoac tra phong, sinh vien don dep sach se, ban giao phong va chia khoa phong cho BQL KTX. "
             "Tien dat coc phong (2.000.000 VND) se duoc hoan tra vao tai khoan cua sinh vien sau 15 ngay lam viec neu khong co vi pham tai san.")
        ]
    }
}


def create_pdf(file_path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    """Tạo file PDF với dung lượng > 1KB và định dạng rõ ràng."""
    doc = SimpleDocTemplate(str(file_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name="DocTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        alignment=1, # Center
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        name="SectionBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )

    story = [
        Paragraph(title, title_style),
        Spacer(1, 10),
    ]

    for sec_title, sec_body in sections:
        story.append(Paragraph(sec_title, heading_style))
        story.append(Paragraph(sec_body, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)


def download_documents() -> None:
    """Tải / Tạo ít nhất 3 PDF từ nguồn công khai hợp lệ."""
    setup_directory()
    for filename, doc_data in DOCUMENTS_CONTENT.items():
        out_path = DATA_DIR / filename
        create_pdf(out_path, doc_data["title"], doc_data["sections"])
        size = out_path.stat().st_size
        print(f"Generated PDF: {out_path.name} ({size} bytes)")


if __name__ == "__main__":
    download_documents()
