import HashMap
import model
import CategoryManager
import CTDL
import TransactionManager

class ReportManager:
    def __init__(self, month_index):
        self._month_index = month_index

    def generate_monthly_report(self, year, month):
        """
        In báo cáo tài chính tháng ra Terminal:
        - Tổng hợp Thu, Chi, Thặng dư trong kỳ.
        - Vẽ biểu đồ tỷ lệ phần trăm chi tiêu giữa các nhóm bằng ký tự văn bản.
        - Liệt kê danh sách các mục chi tiêu vượt hạn mức (Budget).
        """
        # ==========================================
        # 1. TRUY XUẤT DỮ LIỆU THÁNG
        # ==========================================
        month_data = self._month_index.get(year, month)
        
        print("\n" + "="*55)
        print(f"        BÁO CÁO TÀI CHÍNH THÁNG {month:02d}/{year}        ")
        print("="*55)

        if month_data is None:
            print(f" ❌ Không tìm thấy dữ liệu giao dịch nào cho tháng {month:02d}/{year}.")
            print("="*55)
            return

        # ==========================================
        # 2. TỔNG HỢP SỐ LIỆU THU / CHI
        # ==========================================
        total_income = 0
        total_expense = 0
        expense_list = []

        # Quét qua toàn bộ các CategoryState trong tháng thông qua bảng băm
        for state_id in month_data.category_states.keys():
            state = month_data.category_states.get(state_id)
            
            # Phân loại dựa trên thuộc tính type của danh mục gốc (category.type)
            # Đồng bộ xử lý chuỗi chữ thường theo model.py và CategoryManager.py
            cat_type = state.category.type.lower()
            
            if cat_type == "income":
                total_income += state.total_income
            elif cat_type == "expense":
                total_expense += state.total_expense
                if state.total_expense > 0:
                    expense_list.append(state)

        net_savings = total_income - total_expense
        
        print(f" 💰 Tổng thu nhập    : {total_income:,.0f} đ")
        print(f" 💸 Tổng chi tiêu    : {total_expense:,.0f} đ")
        print(f" ⚖️ Thặng dư tích lũy: {net_savings:,.0f} đ " + ("📈" if net_savings >= 0 else "📉"))
        print("-" * 55)

        # ==========================================
        # 3. ĐỒ HỌA CHỮ: TỶ LỆ CHI TIÊU GIỮA CÁC NHÓM
        # ==========================================
        print(" 📊 BIỂU ĐỒ TỶ LỆ CHI TIÊU GIỮA CÁC DANH MỤC:")
        if total_expense == 0:
            print("   (Chưa có dữ liệu chi tiêu để hiển thị biểu đồ)")
        else:
            # Sắp xếp danh mục có số tiền tiêu từ nhiều nhất đến ít nhất
            expense_list.sort(key=lambda x: x.total_expense, reverse=True)
            
            for state in expense_list:
                percentage = (state.total_expense / total_expense) * 100
                
                # Tính độ dài thanh đồ thị (Tối đa 20 ký tự ứng với 100%)
                bar_length = int(percentage / 5)
                bar_visual = "■" * bar_length if bar_length > 0 else "·"
                
                print(f"   • {state.category.name:<15} | {bar_visual:<20} | {percentage:6.1f}% ({state.total_expense:,.0f} đ)")
        print("-" * 55)

        # ==========================================
        # 4. TỔNG HỢP CÁC MỤC VƯỢT BUDGET (NGÂN SÁCH)
        # ==========================================
        print(" ⚠️ DANH SÁCH DANH MỤC VƯỢT NGÂN SÁCH (BUDGET):")
        over_budget_count = 0
        
        for state in expense_list:
            # Lấy chính xác hạn mức lịch sử lưu trong State của tháng đó
            limit = state.limit
            
            if state.total_expense > limit:
                over_budget_count += 1
                amount_over = state.total_expense - limit
                percent_over = (amount_over / limit) * 100 if limit > 0 else 100
                
                print(f"   ❌ [{state.category.name}] ĐÃ VƯỢT HẠN MỨC!")
                print(f"      - Ngân sách đặt ra : {limit:,.0f} đ")
                print(f"      - Thực tế đã chi   : {state.total_expense:,.0f} đ")
                print(f"      - Số tiền vượt quá : +{amount_over:,.0f} đ ({percent_over:.1f}%)")
                print()
                
        if over_budget_count == 0:
            print("   🎉 Tuyệt vời! Bạn đã kiểm soát tốt, không có danh mục nào chi tiêu vượt hạn mức.")
            
        print("="*55 + "\n")