# Неинтерактивные протоколы доказательства с нулевым разглашением
import random

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def modinv(a, m):
    """
    Находит обратное число к a по модулю m (расширенный алгоритм Евклида).
    a * x ≡ 1 (mod m)
    """
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def mod_pow(base, exp, mod):
    """Быстрое возведение в степень по модулю (встроенный pow в Python делает то же самое)."""
    return pow(base, exp, mod)

def egcd(a, b):
    """Расширенный алгоритм Евклида для нахождения НОД и коэффициентов."""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv_extended(a, m):
    """Обратное число через расширенный алгоритм Евклида (работает быстрее перебора)."""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Обратного числа не существует')
    else:
        return x % m

# ---------- ПРОТОКОЛ ЧЕСТНОГО ДОКАЗАТЕЛЬСТВА ----------

class HonestProver:
    """Честный Пэгги, которая знает секрет m."""
    
    def __init__(self, m, N, e):
        self.m = m
        self.N = N
        self.e = e
        self.c = mod_pow(m, e, N)
        print(f"[Инициализация] m = {m}, c = {self.c}")
    
    def generate_proof(self):
        """Генерирует доказательство (x1, x2) по протоколу."""
        # 1. Выбираем случайное r1 (взаимно простое с N, но для RSA это почти всегда так)
        while True:
            r1 = random.randint(2, self.N - 1)
            if egcd(r1, self.N)[0] == 1:
                break
        
        print(f"[Честная Пэгги] Выбрала r1 = {r1}")
        
        # 2. Вычисляем r2 = m * r1^(-1) mod N
        r1_inv = modinv_extended(r1, self.N)
        r2 = (self.m * r1_inv) % self.N
        print(f"[Честная Пэгги] Вычислила r2 = {r2}")
        
        # 3. Вычисляем x1 и x2
        x1 = mod_pow(r1, self.e, self.N)
        x2 = mod_pow(r2, self.e, self.N)
        
        print(f"[Честная Пэгги] Отправляет Виктору: x1 = {x1}, x2 = {x2}")
        return (x1, x2)

class Verifier:
    """Виктор — проверяющий."""
    
    def __init__(self, N, e, c):
        self.N = N
        self.e = e
        self.c = c
    
    def verify(self, x1, x2):
        """Проверяет, что x1 * x2 ≡ c (mod N)."""
        product = (x1 * x2) % self.N
        is_valid = (product == self.c)
        print(f"[Виктор] Проверка: {x1} * {x2} mod {self.N} = {product}")
        print(f"[Виктор] Ожидалось: {self.c}")
        print(f"[Виктор] Результат: {'✅ ДОКАЗАТЕЛЬСТВО ПРИНЯТО' if is_valid else '❌ ОТКЛОНЕНО'}")
        return is_valid

# ---------- ЗЛОУМЫШЛЕННИК (ОБХОД ПРОТОКОЛА) ----------

class MaliciousProver:
    """
    Злоумышленник, который НЕ знает m, но может обмануть Виктора,
    так как протокол не требует доказательства знания r1 и r2.
    """
    
    def __init__(self, N, e, c):
        self.N = N
        self.e = e
        self.c = c
        print(f"[Инициализация атаки] c = {c}")
    
    def generate_fake_proof(self):
        """
        Генерирует фальшивые x1, x2, которые проходят проверку,
        но не требуют знания m.
        Атака: выбираем случайное t, x1 = t ^ e, x2 = c * t ^ (-e)
        """
        # 1. Выбираем случайное t (взаимно простое с N)
        while True:
            t = random.randint(2, self.N - 1)
            if egcd(t, self.N)[0] == 1:
                break
        
        print(f"[Злоумышленник] Выбрал случайное t = {t}")
        
        # 2. Вычисляем x1 = t^e mod N
        x1 = mod_pow(t, self.e, self.N)
        
        # 3. Вычисляем x2 = c * t^(-e) mod N
        t_inv = modinv_extended(t, self.N)
        t_inv_pow = mod_pow(t_inv, self.e, self.N)
        x2 = (self.c * t_inv_pow) % self.N
        
        print(f"[Злоумышленник] Отправляет Виктору: x1 = {x1}, x2 = {x2}")
        print(f"[Злоумышленник] (Он даже не знает m!)")
        return (x1, x2)

# ---------- ДЕМОНСТРАЦИЯ РАБОТЫ ----------

def main():
    print("=" * 60)
    print("НЕИНТЕРАКТИВНЫЙ ПРОТОКОЛ ZKP НА ОСНОВЕ RSA")
    print("=" * 60)
    
    # Параметры RSA (маленькие, чтобы было наглядно)
    # В реальности N должно быть большим, но для примера возьмем простое N,
    # чтобы легко считать обратные числа.
    N = 2430101    # Модуль (в реальности огромное составное число)
    e = 9007       # Открытая экспонента
    m = 88         # Секретное сообщение, которое знает Пэгги
    
    # Вычисляем c = m^e mod N
    c = mod_pow(m, e, N)
    print(f"\nПубличные параметры:")
    print(f"  N = {N}")
    print(f"  e = {e}")
    print(f"  c = {c} (это шифротекст, полученный из m)\n")
    
    # ---------- СЦЕНАРИЙ 1: ЧЕСТНАЯ ПЭГГИ ----------
    print("\n--- Сценарий 1: Честная Пэгги (знает m) ---")
    peggy = HonestProver(m, N, e)
    victor = Verifier(N, e, c)
    
    x1, x2 = peggy.generate_proof()
    victor.verify(x1, x2)
    
    # ---------- СЦЕНАРИЙ 2: ЗЛОУМЫШЛЕННИК ----------
    print("\n--- Сценарий 2: Злоумышленник (НЕ знает m) ---")
    mallory = MaliciousProver(N, e, c)
    fake_x1, fake_x2 = mallory.generate_fake_proof()
    
    # Виктор проверяет теми же глазами
    victor.verify(fake_x1, fake_x2)
    
    print("\n" + "=" * 60)
    print("ВЫВОД: Протокол уязвим! Злоумышленник обманул Виктора,")
    print("не зная m, потому что проверка x1 * x2 ≡ c не требует")
    print("доказательства знания r1 и r2.")
    print("=" * 60)

if __name__ == "__main__":
    main()