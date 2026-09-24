using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Common.Enums;
using FirstAPIProject.Domain.Constants;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence;

public static class DatabaseSeeder
{
    public static async Task SeedAsync(
        AppDbContext context,
        IPasswordService passwordService )
    {
        var defaultPasswordHash = passwordService.HashPassword("Student@123");
        var adminPasswordHash = passwordService.HashPassword("Admin@123");

        // =========================================================================
        // 1. SEED ADMINS
        // =========================================================================
        var admin = await context.Users.FirstOrDefaultAsync(x => x.Email == "admin@system.com");
        if (admin == null)
        {
            admin = User.Create(
                email: "admin@system.com",
                passwordHash: adminPasswordHash,
                roleId: SystemRoleIds.Admin,
                userName: "admin",
                phoneNumber: "0900000001");
            admin.UpdateProfile("admin", "0900000001", "Phong Du lieu & CNTT, Toa nha A, UIT", Gender.Male, new DateOnly(1990, 1, 1));
            admin.VerifyEmail();
            context.Users.Add(admin);
            await context.SaveChangesAsync();
        }
        else if (!admin.IsEmailVerified)
        {
            admin.VerifyEmail();
            await context.SaveChangesAsync();
        }

        if (!await context.Users.AnyAsync(x => x.Email == "admin2@system.com"))
        {
            var admin2 = User.Create(
                email: "admin2@system.com",
                passwordHash: adminPasswordHash,
                roleId: SystemRoleIds.Admin,
                userName: "admin_daotao",
                phoneNumber: "0900000002");
            admin2.UpdateProfile("admin_daotao", "0900000002", "Phong Dao tao Dai hoc, Toa nha A, UIT", Gender.Female, new DateOnly(1992, 5, 20));
            admin2.VerifyEmail();
            context.Users.Add(admin2);
        }

        // =========================================================================
        // 2. SEED UIT & VNU-HCM STUDENTS (Test phan trang, tim kiem, loc trang thai)
        // =========================================================================
        var studentProfiles = new[]
        {
            // Tai khoan sinh vien chuan mac dinh de FE test de dang
            new { Email = "student@uit.edu.vn", UserName = "nguyen_van_a", Name = "Nguyen Van An", Phone = "0901234567", Address = "KTX Khu B DHQG-HCM, Toa B3, Linh Trung, TP Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2003, 9, 15), Status = UserStatus.Normal, Verified = true },
            new { Email = "21520001@gm.uit.edu.vn", UserName = "le_thi_b", Name = "Le Thi Bich", Phone = "0912345678", Address = "KTX Khu A DHQG-HCM, Linh Trung, TP Thu Duc", Gender = Gender.Female, Dob = new DateOnly(2003, 3, 20), Status = UserStatus.Normal, Verified = true },
            new { Email = "21520115@gm.uit.edu.vn", UserName = "tran_cuong", Name = "Tran Hoang Cuong", Phone = "0923456789", Address = "Duong Han Thuyen, Khu pho 6, Linh Trung, Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2003, 11, 8), Status = UserStatus.Normal, Verified = true },
            new { Email = "22520228@gm.uit.edu.vn", UserName = "pham_dung", Name = "Pham Minh Dung", Phone = "0934567890", Address = "Khu dan cu Lang Dai hoc, Dong Hoa, Di An", Gender = Gender.Male, Dob = new DateOnly(2004, 4, 12), Status = UserStatus.Normal, Verified = true },
            new { Email = "22520340@gm.uit.edu.vn", UserName = "hoang_linh", Name = "Hoang Thuy Linh", Phone = "0945678901", Address = "Toa C1 KTX Khu B, Linh Trung, TP Thu Duc", Gender = Gender.Female, Dob = new DateOnly(2004, 7, 25), Status = UserStatus.Normal, Verified = true },
            new { Email = "23520455@gm.uit.edu.vn", UserName = "vu_huy", Name = "Vu Quoc Huy", Phone = "0956789012", Address = "Duong so 8, Linh Xuan, TP Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2005, 1, 30), Status = UserStatus.Normal, Verified = true },
            new { Email = "23520560@gm.uit.edu.vn", UserName = "dang_mai", Name = "Dang Ngoc Mai", Phone = "0967890123", Address = "Toa E1 KTX Khu B DHQG-HCM, Linh Trung", Gender = Gender.Female, Dob = new DateOnly(2005, 10, 5), Status = UserStatus.Normal, Verified = true },
            new { Email = "21520670@gm.uit.edu.vn", UserName = "bui_nam", Name = "Bui Phuong Nam", Phone = "0978901234", Address = "Phuong Hiep Phu, TP Thu Duc, TP Ho Chi Minh", Gender = Gender.Male, Dob = new DateOnly(2003, 6, 18), Status = UserStatus.Normal, Verified = true },
            new { Email = "22520780@gm.uit.edu.vn", UserName = "do_phuc", Name = "Do Hong Phuc", Phone = "0989012345", Address = "KTX Khu A, Linh Trung, TP Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2004, 8, 22), Status = UserStatus.Normal, Verified = true },
            new { Email = "22520890@gm.uit.edu.vn", UserName = "ngo_thinh", Name = "Ngo Gia Thinh", Phone = "0990123456", Address = "Duong Quang Trung, Tang Nhon Phu B, Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2004, 12, 14), Status = UserStatus.Normal, Verified = true },
            new { Email = "23520910@gm.uit.edu.vn", UserName = "trinh_nhi", Name = "Trinh Thao Nhi", Phone = "0909876543", Address = "Toa D5 KTX Khu B DHQG-HCM", Gender = Gender.Female, Dob = new DateOnly(2005, 2, 9), Status = UserStatus.Normal, Verified = true },
            new { Email = "tuan.da@hcmut.edu.vn", UserName = "duong_tuan", Name = "Duong Anh Tuan", Phone = "0918765432", Address = "KTX Bach Khoa, Quan 10, TP Ho Chi Minh", Gender = Gender.Male, Dob = new DateOnly(2003, 5, 17), Status = UserStatus.Normal, Verified = true },
            new { Email = "thao.ct@hcmus.edu.vn", UserName = "cao_thao", Name = "Cao Thanh Thao", Phone = "0927654321", Address = "Nguyen Van Cu, Quan 5, TP Ho Chi Minh", Gender = Gender.Female, Dob = new DateOnly(2004, 9, 3), Status = UserStatus.Normal, Verified = true },
            
            // Tai khoan khoa (Locked) de FE test nut Mo khoa & giao dien chan dang nhap
            new { Email = "locked_student@uit.edu.vn", UserName = "locked_user", Name = "Sinh Vien Bi Khoa 1", Phone = "0988888888", Address = "Linh Trung, TP Thu Duc", Gender = Gender.Male, Dob = new DateOnly(2003, 1, 1), Status = UserStatus.Locked, Verified = true },
            new { Email = "locked_student2@gm.uit.edu.vn", UserName = "locked_user2", Name = "Sinh Vien Vi Pham 2", Phone = "0977777777", Address = "Linh Xuan, TP Thu Duc", Gender = Gender.Female, Dob = new DateOnly(2004, 12, 12), Status = UserStatus.Locked, Verified = true },
            
            // Tai khoan chua xac thuc Email (Unverified) de test luong verify OTP
            new { Email = "unverified@uit.edu.vn", UserName = "unverified_user", Name = "Sinh Vien Chua Verify", Phone = "0966666666", Address = "Lang Dai hoc, Linh Trung", Gender = Gender.Male, Dob = new DateOnly(2005, 4, 1), Status = UserStatus.Normal, Verified = false }
        };

        foreach (var p in studentProfiles)
        {
            if (!await context.Users.AnyAsync(x => x.Email == p.Email))
            {
                var s = User.Create(
                    email: p.Email,
                    passwordHash: defaultPasswordHash,
                    roleId: SystemRoleIds.Student,
                    userName: p.UserName,
                    phoneNumber: p.Phone);

                s.UpdateProfile(
                    userName: p.UserName,
                    phoneNumber: p.Phone,
                    address: p.Address,
                    gender: p.Gender,
                    dateOfBirth: p.Dob);

                if (p.Verified)
                {
                    s.VerifyEmail();
                }

                if (p.Status == UserStatus.Locked)
                {
                    s.Lock();
                }

                context.Users.Add(s);
            }
        }

        await context.SaveChangesAsync();

        // =========================================================================
        // 3. SEED EMAIL WHITELIST (UIT, DHQG-HCM, Bach Khoa, KHTN, v.v.)
        // =========================================================================
        var whitelistDomains = new[]
        {
            new { Domain = "uit.edu.vn", Active = true },
            new { Domain = "gm.uit.edu.vn", Active = true },
            new { Domain = "vnuhcm.edu.vn", Active = true },
            new { Domain = "hcmut.edu.vn", Active = true },
            new { Domain = "hcmus.edu.vn", Active = true },
            new { Domain = "uel.edu.vn", Active = true },
            new { Domain = "test.com", Active = true },
            new { Domain = "old-partner.edu.vn", Active = false },
            new { Domain = "expired-domain.com", Active = false }
        };

        foreach (var item in whitelistDomains)
        {
            if (!await context.EmailWhitelists.AnyAsync(x => x.Domain == item.Domain))
            {
                var entry = EmailWhitelist.ForDomain(item.Domain, admin.Id);
                if (!item.Active)
                {
                    entry.Deactivate();
                }
                context.EmailWhitelists.Add(entry);
            }
        }

        var whitelistEmails = new[]
        {
            new { Email = "vip.student@gmail.com", Active = true },
            new { Email = "researcher.guest@gmail.com", Active = true },
            new { Email = "alumni.scholarship@gmail.com", Active = true },
            new { Email = "inactive.tester@gmail.com", Active = false }
        };

        foreach (var item in whitelistEmails)
        {
            if (!await context.EmailWhitelists.AnyAsync(x => x.Email == item.Email))
            {
                var entry = EmailWhitelist.ForEmail(item.Email, admin.Id);
                if (!item.Active)
                {
                    entry.Deactivate();
                }
                context.EmailWhitelists.Add(entry);
            }
        }

        await context.SaveChangesAsync();

        // =========================================================================
        // 4. SEED ANNOUNCEMENTS (Thong bao UIT & DHQG)
        // =========================================================================
        var announcementsToSeed = new[]
        {
            new {
                Title = "Chao mung tan sinh vien Khoa 2026 - Truong DH Cong nghe Thong tin (UIT)",
                Content = "Chao mung toan the tan sinh viên K2026 da gia nhap ngoi nha chung UIT! Le khai giang nam hoc moi se duoc to chuc trang trong vao luc 08:00 ngay 05/10/2026 tai Hoi truong E, Truong DH Cong nghe Thong tin - DHQG-HCM.",
                Audience = Audience.PUBLIC,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Thong bao lich thi ket thuc hoc phan Hoc ky 1 tai Giang duong A & C",
                Content = "Sinh vien chu y theo doi so bao danh, gio thi va phong thi tren cong thong tin sinh vien. Moi truong hop trung lich thi vui long lien he Phong Dao tao (Phong A120) truoc ngay 15/12/2026.",
                Audience = Audience.STUDENT,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Chuong trinh hoc bong Khuyen khich hoc tap UIT ky 1 nam hoc 2026 - 2027",
                Content = "Phong Cong tac Sinh vien (CTSV) thong bao xet cap hoc bong KKHT danh cho sinh vien co ket qua hoc tap va diem ren luyen loai Gioi tro len trong hoc ky vua qua. Han chot nop ho so: 20/10/2026.",
                Audience = Audience.STUDENT,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Ngay hoi viec lam UIT Career Day 2026 va ket noi doanh nghiep",
                Content = "Hon 40 doanh nghiep cong nghe hang dau trong va ngoai nuoc se tham gia tuyen dung truc tiep ky su phan mem, an toan thong tin, data engineer va AI engineer vao ngay 12/11/2026 tai San Toa nha A, UIT.",
                Audience = Audience.PUBLIC,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Cuoc thi UIT Hackathon 2026: Sang tao giai phap AI & Cloud Computing",
                Content = "Doan Thanh nien - Hoi Sinh vien UIT phat dong cuoc thi lap trinh Hackathon 2026 voi tong giai thuong len den 150 trieu dong. Cac doi thi tu 3-5 thanh vien dang ky truoc ngay 25/10/2026.",
                Audience = Audience.STUDENT,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Thong bao lich nghi le Quoc khanh 02/09 va Lịch Khai giang DHQG-HCM",
                Content = "Toan the can bo, giang vien va sinh vien duoc nghi le theo quy dinh cua Nha nuoc. Le Khai giang nam hoc moi cua khoi Dai hoc Quoc gia TP.HCM se dien ra tai Nha van hoa Sinh vien (Lang Dai hoc).",
                Audience = Audience.PUBLIC,
                Status = PublicationStatus.PUBLISHED
            },
            new {
                Title = "Du thao quy che danh gia diem ren luyen sinh vien UIT nam 2026",
                Content = "Phong Cong tac Sinh vien mo cong lay y kien dong gop cua toan the sinh vien ve bang diem ren luyen cap nhat moi tai phong A104.",
                Audience = Audience.STUDENT,
                Status = PublicationStatus.DRAFT
            },
            new {
                Title = "Ke hoach kham suc khoe dinh ky cho tan sinh vien tai Tram Y te DHQG",
                Content = "Lich kham suc khoe tong quat bat buoc cho sinh vien khoa moi duoc bo tri theo tung khoa tai Trung tam Y te DHQG-HCM (Doi dien KTX Khu A).",
                Audience = Audience.STUDENT,
                Status = PublicationStatus.DRAFT
            },
            new {
                Title = "Thong bao tam dung he thong mang Wi-Fi khu vuc Giang duong C (Da hoan tat)",
                Content = "Khu vuc Giang duong C da duoc nang cap he thong Access Point Wi-Fi 6 vao cuoi tuan. Hien tai sinh vien co the ket noi binh thuong bang email @gm.uit.edu.vn.",
                Audience = Audience.PUBLIC,
                Status = PublicationStatus.ARCHIVED
            }
        };

        foreach (var ann in announcementsToSeed)
        {
            if (!await context.Announcements.AnyAsync(x => x.Title == ann.Title))
            {
                var a = Announcement.Create(ann.Title, ann.Content, ann.Audience, admin.Id);
                if (ann.Status == PublicationStatus.PUBLISHED)
                {
                    a.Publish();
                }
                else if (ann.Status == PublicationStatus.ARCHIVED)
                {
                    a.Publish();
                    a.Archive();
                }
                context.Announcements.Add(a);
            }
        }

        await context.SaveChangesAsync();
    }
}
