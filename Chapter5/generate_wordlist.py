import itertools
import random

# لیست نام‌های رایج ایرانی (مردانه و زنانه)
first_names = [
    "Mohammad", "Ali", "Hossein", "Reza", "Mehdi", "Mahmoud", "Ahmad", "Hassan",
    "Ehsan", "Mohsen", "Saeid", "Majid", "Kaveh", "Behzad", "Amir", "Javad",
    "Hamed", "Khosrow", "Babak", "Dariush", "Fatemeh", "Zahra", "Maryam", "Sara",
    "Narges", "Farzaneh", "Elham", "Leila", "Mahsa", "Shirin", "Parisa", "Asal",
    "Hanieh", "Reyhaneh", "Azadeh", "Neda", "Mina", "Samira", "Shiva", "Nazanin"
]

# لیست نام‌خانوادگی‌های رایج ایرانی
last_names = [
    "Hosseini", "Mohammadi", "Ahmadi", "Rahimi", "Karimi", "Ghasemi", "Ebrahimi",
    "Moradi", "Yousefi", "Ramezani", "Sadeghi", "Jafari", "Hashemi", "Khodadadi",
    "Zare", "Nouri", "Fathi", "Ghaffari", "Soltani", "Kiani", "Shariati", "Mousavi",
    "Rostami", "Hosseinzadeh", "Alizadeh"
]

# لیست سال‌های تولد و اعداد رایج
years = [str(year) for year in range(1360, 1405)]
numbers = ["123", "1234", "12345", "2020", "2021", "2022", "2023", "2024", "2025"]
suffixes = ["admin", "user", "editor", "test"]

# فرمت‌های مختلف برای ترکیبات
formats = [
    "{first}_{last}", "{first}{last}", "{first}.{last}", "{first}-{last}",
    "{first}_{last_lower}", "{first_lower}_{last_lower}", "{first_lower}{last_lower}",
    "{first_lower}.{last_lower}", "{first_lower}-{last_lower}",
    "{first}_{year}", "{first}{year}", "{first}_{number}", "{first}{number}",
    "{first_lower}_{year}", "{first_lower}{year}", "{first_lower}_{number}", "{first_lower}{number}"
]

def generate_usernames(output_file, target_count=1000000):
    with open(output_file, 'w', encoding='utf-8') as f:
        generated = 0
        # ترکیبات نام و نام‌خانوادگی
        for first, last in itertools.product(first_names, last_names):
            for fmt in formats[:9]:  # فرمت‌های مربوط به نام و نام‌خانوادگی
                username = fmt.format(
                    first=first, last=last,
                    first_lower=first.lower(), last_lower=last.lower()
                )
                f.write(username + '\n')
                generated += 1
                if generated >= target_count:
                    return generated
        
        # ترکیبات نام با سال و اعداد
        for first in first_names:
            for item in years + numbers:
                for fmt in formats[9:]:  # فرمت‌های مربوط به سال و اعداد
                    username = fmt.format(
                        first=first, year=item, number=item,
                        first_lower=first.lower()
                    )
                    f.write(username + '\n')
                    generated += 1
                    if generated >= target_count:
                        return generated
        
        # اضافه کردن موارد پیش‌فرض
        for suffix in suffixes:
            f.write(suffix + '\n')
            generated += 1
            if generated >= target_count:
                return generated
        
        # پر کردن باقی‌مانده با ترکیبات تصادفی (در صورت نیاز)
        while generated < target_count:
            first = random.choice(first_names)
            last = random.choice(last_names + years + numbers)
            fmt = random.choice(formats)
            username = fmt.format(
                first=first, last=last, year=last, number=last,
                first_lower=first.lower(), last_lower=last.lower()
            )
            f.write(username + '\n')
            generated += 1
    
    return generated

if __name__ == '__main__':
    output_file = '/home/kalafe/bhp/Chapter5/wordpress.txt'
    target_count = 2000000  # هدف 2 میلیون username
    print(f"Generating wordlist with {target_count} usernames...")
    count = generate_usernames(output_file, target_count)
    print(f"Generated {count} usernames in {output_file}")