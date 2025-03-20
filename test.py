from colorama import init, Fore, Style
from termcolor import colored
import random

# Inisialisasi colorama
init(autoreset=True)

# Teks yang akan ditampilkan
text = "Excited to share my achievement in completing the Google Technical Support Fundamentals course on Coursera! 🎓 This training provided essential knowledge in troubleshooting, networking, system administration, security, and more—key skills for a solid start in the IT support field."

# Daftar warna yang tersedia di termcolor
colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# Cetak teks dengan warna yang berubah setiap kata
colored_text = " ".join([colored(word, random.choice(colors)) for word in text.split()])
print(colored_text)
