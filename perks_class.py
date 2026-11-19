import random


class perk:
    def __init__(self, name="Перк", desc="Перк крутой", value=None, chance=20, id=-1, imunitet=False, instant_use=False, const_val=None):
        self.value = value        
        self.name = name
        self.desc = desc
        self.chance = chance
        self.imunitet = imunitet
        self.instant_use = instant_use
        self.const_val = const_val
        self.id = id
    
    def dict_perk(self):
        return {"value": self.value, "id": self.id, "imunitet": self.imunitet, "instant_use": self.instant_use}
    
val = 1
registered_perks = [
perk(name="Гарант на рост", desc="Твой писюн гарантировано вырастит.\nОтрицательные значения игнорируются."),
perk(name="Проклятие Максимки", desc="Твой писюн гарантировано сократится. Положительные значения ингорируются", chance=10),
perk(name="Доп. Прокрутка", desc="Твой писюнчик дополнительно прокрутился.", chance=10, instant_use=True),
perk(name="Уменьши писюн любому", desc="Выбери любого игрока, чтобы уменьшить ему писюнчик", chance=7, imunitet=True, instant_use=False),
perk(name=f"Прибавка к прокрутке", chance=36),
perk(name="Копирка у рандомыча", chance=6),
perk(name="Прошлая дельта", desc="В следующей прокрутке писюна тебе выпадет такое же значение как в прошлой", chance=6),
perk(name="Проверка на короля", const_val=10, chance=6),
perk(name="В", chance=0)
]

count = 0
for i in registered_perks:
    i.id = count
    count+=1



perks_chance_weight = [p.chance for p in registered_perks]


def get_random_perk():
    return random.choices(registered_perks, weights=perks_chance_weight, k=1)[0]

def get_perk_id(perk):
    return registered_perks.index(perk)



def rand_x(prk):
    values = list(range(-5, 11))
    values.remove(0)
    weights = [3, 6, 7, 25, 50, 50, 25, 12, 7, 6, 5, 4, 3, 2, 1]
    rand_celoe = random.choices(values, weights=weights, k=1)[0]
    prk.value = rand_celoe
    prk.desc = f"После прокрутки писюна дельта изменится на *{prk.value} см.*"
    return prk

def rand_minus_pis(prk):
    range_a = list(range(-10, 0))
    weights = [4, 7, 8, 10, 26, 50, 50, 40, 15, 6]
    rand_num = str(random.choices(range_a, weights=weights, k=1)[0])
    dopolnenie = ""
    b = 41
    if rand_num == "-10" and (random.randrange(1, b) == 1):
        rand_num = "-36"
        dopolnenie = f"\nШанс на такое событие ~{round(((1/(b-1))*(weights[0]/sum(weights)))*100, 2)}%"
    prk.value = abs(int(rand_num))
    prk.desc = f"Выбери любого игрока, чтобы уменьшить ему писюнчик на *{prk.value} см.*"+dopolnenie
    return prk


print(rand_x(registered_perks[4]).value)  