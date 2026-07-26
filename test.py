def tinh_toan(a, b, phép_tính):
    if phép_tính == '+':
        return a + b
    elif phép_tính == '-':
        return a - b
    elif phép_tính == '*':
        return a * b
    elif phép_tính == '/':
        return a / b if b != 0 else "Lỗi: Không thể chia cho 0"
    else:
        return "Phép tính không hợp lệ"

if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH TÍNH TOÁN ĐƠN GIẢN ===")
    x = 10
    y = 5
    
    print(f"Số thứ nhất: {x}")
    print(f"Số thứ hai: {y}")
    print(f"Cộng: {x} + {y} = {tinh_toan(x, y, '+')}")
    print(f"Trừ: {x} - {y} = {tinh_toan(x, y, '-')}")
    print(f"Nhân: {x} * {y} = {tinh_toan(x, y, '*')}")
    print(f"Chia: {x} / {y} = {tinh_toan(x, y, '/')}")