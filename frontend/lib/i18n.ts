export type AppLanguage = "vi" | "en";

const messages = {
  vi: {
    settings: "Cài đặt Hệ thống (Settings)", settingsDescription: "Quản lý tài khoản, trải nghiệm trò chuyện, quyền riêng tư, thông báo và giao diện ứng dụng.",
    configureAi: "Cấu hình AI Hub", editProfile: "Chỉnh sửa Hồ sơ cá nhân", accountSecurity: "Tài khoản & Bảo mật",
    chatsMedia: "Trò chuyện & Media", privacy: "Quyền riêng tư", notifications: "Thông báo & Âm thanh", navNotifications: "Thông báo",
    appearance: "Giao diện & Ngôn ngữ", about: "Về ứng dụng", appearanceTitle: "Giao diện & Ngôn ngữ (Appearance)",
    themeMode: "Chế độ hiển thị (Theme Mode)", light: "Sáng", dark: "Tối", system: "Hệ thống",
    accentColor: "Màu sắc chủ đạo (Accent Color)", blue: "Xanh dương", emerald: "Xanh lục", purple: "Tím", indigo: "Chàm", amber: "Hổ phách",
    displayLanguage: "Ngôn ngữ hiển thị (Language)", languageHelp: "Chọn ngôn ngữ cho toàn bộ ứng dụng.",
    vietnamese: "Tiếng Việt (Mặc định)", english: "English (US)", chats: "Trò chuyện", connections: "Kết nối",
    copilot: "Copilot", navSettings: "Cài đặt", logout: "Đăng xuất", profile: "Hồ sơ cá nhân", viewEditProfile: "Xem & Chỉnh sửa hồ sơ",
    accountInfo: "Thông tin Tài khoản", active: "Đang hoạt động", fullName: "Họ và tên", unnamed: "Chưa đặt tên", loginEmail: "Email đăng nhập",
    phone: "Số điện thoại", notLinked: "Chưa liên kết", profession: "Chức danh / Vị trí", notUpdated: "Chưa cập nhật", editProfilePage: "Chỉnh sửa hồ sơ tại trang Profile →",
    changePassword: "Đổi Mật khẩu", currentPassword: "Mật khẩu hiện tại", currentPasswordPlaceholder: "Nhập mật khẩu đang dùng", newPassword: "Mật khẩu mới",
    minimumSix: "Tối thiểu 6 ký tự", confirmPassword: "Xác nhận mật khẩu mới", confirmPasswordPlaceholder: "Nhập lại mật khẩu mới", processing: "Đang xử lý...", updatePassword: "Cập nhật Mật khẩu",
    sessions: "Phiên Đăng nhập & Thiết bị", currentBrowser: "Trình duyệt Hiện tại (Web Browser)", onlineLocal: "Đang trực tuyến • Địa chỉ IP mạng nội bộ", thisDevice: "Thiết bị này",
    chatBehavior: "Hành vi Trò chuyện (Chat Behavior)", enterSend: "Bấm phím Enter để gửi tin nhắn", enterHelp: "Khi bật: Bấm Enter để gửi ngay, Shift + Enter để xuống dòng mới.",
    autoMedia: "Tự động tải phương tiện (Media)", autoMediaHelp: "Tự động hiển thị trước và tải hình ảnh, tài liệu đính kèm trong phòng chat.", chatFont: "Cỡ chữ trong khung chat",
    chatFontHelp: "Điều chỉnh kích thước hiển thị của bong bóng tin nhắn.", small: "Nhỏ (13px)", standard: "Tiêu chuẩn (14px)", large: "Lớn (16px)",
    storage: "Dữ liệu & Bộ nhớ tạm", clearLocalCache: "Xóa bộ nhớ đệm trò chuyện trên máy", clearCacheHelp: "Giải phóng dung lượng bản nháp và bộ đệm tin nhắn cục bộ.", clearCache: "Xóa Cache",
    privacyVisibility: "Quyền Riêng tư & Hiển thị", publicProfile: "Chế độ Công khai Hồ sơ (Public Profile)", publicProfileHelp: "Cho phép người dùng khác tìm kiếm hồ sơ và gửi lời mời kết nối tới bạn.",
    readReceipts: "Hiển thị trạng thái \"Đã xem\" (Read Receipts)", readReceiptsHelp: "Cho phép đối phương biết khi bạn đã đọc tin nhắn của họ.", onlineStatus: "Trạng thái Hoạt động (Online Status)",
    onlineStatusHelp: "Hiển thị chấm xanh báo hiệu bạn đang trực tuyến hoặc vừa mới truy cập.", blockedUsers: "Danh sách Người dùng đã Chặn", noBlockedUsers: "Bạn chưa chặn người dùng nào.", unblock: "Bỏ chặn",
    notificationsTitle: "Thông báo & Âm báo (Notifications)", pushNotifications: "Bật thông báo đẩy (Push Notifications)", pushHelp: "Nhận thông báo khi có tin nhắn mới, lời mời kết nối hoặc gợi ý AI.",
    incomingSound: "Âm thanh Tin nhắn đến", soundHelp: "Phát âm thanh thông báo chuông khi nhận được tin nhắn mới.", messagePreview: "Hiển thị trước Nội dung tin nhắn", previewHelp: "Hiển thị tên người gửi và đoạn trích tin nhắn trong cửa sổ thông báo pop-up.",
    appTagline: "Nền tảng nhắn tin thông minh tích hợp Trợ lý AI Multi-Agent", appVersion: "Phiên bản ứng dụng", aiArchitecture: "Kiến trúc AI", database: "Cơ sở dữ liệu",
    copyright: "© 2026 MemoryChat Platform. Được thiết kế và bảo vệ theo tiêu chuẩn bảo mật dữ liệu người dùng.",
    systemSettingsTitle: "Cài đặt hệ thống", profileTitle: "Hồ sơ cá nhân", all: "Tất cả", unread: "Chưa đọc",
    chatsTitle: "Đoạn chat (Chats)", searchChats: "Tìm kiếm cuộc trò chuyện...", noUnreadMessages: "Không có tin nhắn chưa đọc.",
    noConversations: "Chưa có cuộc trò chuyện nào.", noMessages: "Chưa có tin nhắn nào", online: "Đang hoạt động", offline: "Không hoạt động",
    yourConversations: "Cuộc trò chuyện của bạn", selectConversationHelp: "Chọn một người bạn từ danh sách bên trái hoặc khám phá các gợi ý kết nối để bắt đầu trò chuyện.",
    viewPeerInfo: "Xem thông tin đối phương", openCopilot: "Mở AI Copilot", closeInfo: "Đóng thông tin", openInfo: "Mở thông tin", moreOptions: "Tùy chọn khác",
    viewProfile: "Xem trang cá nhân", unfriend: "Hủy kết bạn", unfriendSuccess: "Đã hủy kết bạn thành công.", unfriendError: "Lỗi khi hủy kết bạn.",
    emptyConversation: "Chưa có tin nhắn nào trong cuộc trò chuyện này. Hãy gửi lời chào đầu tiên!", loadingMore: "Đang tải thêm tin nhắn...", scrollForMore: "Cuộn để xem thêm",
  },
  en: {
    settings: "System Settings", settingsDescription: "Manage your account, chat experience, privacy, notifications, and application appearance.",
    configureAi: "Configure AI Hub", editProfile: "Edit Profile", accountSecurity: "Account & Security",
    chatsMedia: "Chats & Media", privacy: "Privacy", notifications: "Notifications & Sound", navNotifications: "Notifications",
    appearance: "Appearance & Language", about: "About", appearanceTitle: "Appearance & Language",
    themeMode: "Theme Mode", light: "Light", dark: "Dark", system: "System",
    accentColor: "Accent Color", blue: "Blue", emerald: "Emerald", purple: "Purple", indigo: "Indigo", amber: "Amber",
    displayLanguage: "Display Language", languageHelp: "Choose the language used throughout the application.",
    vietnamese: "Vietnamese", english: "English (US)", chats: "Chats", connections: "Connections",
    copilot: "Copilot", navSettings: "Settings", logout: "Log out", profile: "Profile", viewEditProfile: "View and edit profile",
    accountInfo: "Account Information", active: "Active", fullName: "Full name", unnamed: "Not set", loginEmail: "Login email",
    phone: "Phone number", notLinked: "Not linked", profession: "Job title / Position", notUpdated: "Not updated", editProfilePage: "Edit profile on the Profile page →",
    changePassword: "Change Password", currentPassword: "Current password", currentPasswordPlaceholder: "Enter your current password", newPassword: "New password",
    minimumSix: "At least 6 characters", confirmPassword: "Confirm new password", confirmPasswordPlaceholder: "Re-enter your new password", processing: "Processing...", updatePassword: "Update Password",
    sessions: "Login Sessions & Devices", currentBrowser: "Current Browser", onlineLocal: "Online • Local network IP address", thisDevice: "This device",
    chatBehavior: "Chat Behavior", enterSend: "Press Enter to send messages", enterHelp: "When enabled: press Enter to send and Shift + Enter for a new line.",
    autoMedia: "Automatically download media", autoMediaHelp: "Automatically preview and download images and attachments in chats.", chatFont: "Chat font size",
    chatFontHelp: "Adjust the display size of message bubbles.", small: "Small (13px)", standard: "Standard (14px)", large: "Large (16px)",
    storage: "Data & Cache", clearLocalCache: "Clear local chat cache", clearCacheHelp: "Free space used by local drafts and cached messages.", clearCache: "Clear Cache",
    privacyVisibility: "Privacy & Visibility", publicProfile: "Public Profile", publicProfileHelp: "Allow other users to find your profile and send connection requests.",
    readReceipts: "Read Receipts", readReceiptsHelp: "Let other people know when you have read their messages.", onlineStatus: "Online Status",
    onlineStatusHelp: "Show an indicator when you are online or were recently active.", blockedUsers: "Blocked Users", noBlockedUsers: "You have not blocked anyone.", unblock: "Unblock",
    notificationsTitle: "Notifications & Sound", pushNotifications: "Push Notifications", pushHelp: "Receive notifications for new messages, connection requests, and AI suggestions.",
    incomingSound: "Incoming Message Sound", soundHelp: "Play a notification sound when a new message arrives.", messagePreview: "Message Preview", previewHelp: "Show the sender name and a message excerpt in notifications.",
    appTagline: "Intelligent messaging powered by a multi-agent AI assistant", appVersion: "Application version", aiArchitecture: "AI architecture", database: "Database",
    copyright: "© 2026 MemoryChat Platform. Designed and protected according to user data security standards.",
    systemSettingsTitle: "System settings", profileTitle: "Profile", all: "All", unread: "Unread",
    chatsTitle: "Chats", searchChats: "Search conversations...", noUnreadMessages: "No unread messages.",
    noConversations: "No conversations yet.", noMessages: "No messages yet", online: "Online", offline: "Offline",
    yourConversations: "Your conversations", selectConversationHelp: "Select a friend from the list or explore connection suggestions to start a conversation.",
    viewPeerInfo: "View contact information", openCopilot: "Open AI Copilot", closeInfo: "Close information", openInfo: "Open information", moreOptions: "More options",
    viewProfile: "View profile", unfriend: "Unfriend", unfriendSuccess: "Friend removed successfully.", unfriendError: "Could not remove friend.",
    emptyConversation: "There are no messages in this conversation yet. Send the first hello!", loadingMore: "Loading more messages...", scrollForMore: "Scroll to see more",
  },
} as const;

export type TranslationKey = keyof typeof messages.vi;

export function getLanguage(language?: string): AppLanguage {
  return language === "en" ? "en" : "vi";
}

export function translate(language: AppLanguage, key: TranslationKey): string {
  return messages[language][key];
}
