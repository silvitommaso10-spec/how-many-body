#!/usr/bin/env python3
"""
Generatore del dataset di personaggi storici per il gioco "Higher or Lower".
Ogni personaggio ha 3 valori (approssimativi / a scopo ludico):
  - kills:     numero di morti attribuite (guerre, ordini, campagne)
  - women:     numero di donne / mogli / concubine / partner note
  - territory: territorio conquistato / governato in km2 (picco di estensione)

I valori delle figure molto famose sono impostati a mano; per le altre figure
storiche reali i valori sono assegnati in modo deterministico (seed = nome)
entro intervalli plausibili per la loro "scala" storica, in modo che restino
stabili, distinti e confrontabili tra loro.
"""

import hashlib
import json

# ---------------------------------------------------------------------------
# Valori impostati a mano per le figure iconiche (kills, women, territory_km2)
# ---------------------------------------------------------------------------
FAMOUS = {
    "Gengis Khan":            (40_000_000, 3000, 24_000_000),
    "Alessandro Magno":       (1_500_000,  360,  5_200_000),
    "Giulio Cesare":          (1_200_000,  100,  1_900_000),
    "Napoleone Bonaparte":    (5_000_000,  40,   2_100_000),
    "Adolf Hitler":           (17_000_000, 3,    3_000_000),
    "Iosif Stalin":           (20_000_000, 4,    22_400_000),
    "Mao Zedong":             (40_000_000, 50,   9_600_000),
    "Tamerlano":              (17_000_000, 100,  4_400_000),
    "Attila":                 (1_000_000,  30,   4_000_000),
    "Qin Shi Huang":          (1_000_000,  3000, 2_300_000),
    "Ashoka":                 (500_000,    500,  5_000_000),
    "Ciro il Grande":         (400_000,    360,  5_500_000),
    "Dario I":                (300_000,    360,  5_500_000),
    "Serse I":                (500_000,    360,  5_500_000),
    "Annibale":               (300_000,    5,    200_000),
    "Scipione l'Africano":    (250_000,    3,    150_000),
    "Carlo Magno":            (400_000,    18,   1_200_000),
    "Guglielmo il Conquistatore": (100_000, 10,  150_000),
    "Saladino":               (300_000,    16,   2_000_000),
    "Riccardo Cuor di Leone": (100_000,    2,    250_000),
    "Vlad l'Impalatore":      (100_000,    3,    50_000),
    "Ivan il Terribile":      (500_000,    8,    5_400_000),
    "Pietro il Grande":       (400_000,    3,    15_800_000),
    "Caterina la Grande":     (200_000,    22,   17_000_000),
    "Solimano il Magnifico":  (1_000_000,  300,  4_500_000),
    "Maometto II":            (300_000,    200,  2_200_000),
    "Selim I":                (400_000,    200,  1_500_000),
    "Osman I":                (50_000,     100,  16_000),
    "Kublai Khan":            (5_000_000,  7000, 14_000_000),
    "Hulagu Khan":            (2_000_000,  500,  8_000_000),
    "Batu Khan":              (2_000_000,  200,  6_000_000),
    "Subutai":                (2_000_000,  10,   0),
    "Akbar":                  (500_000,    5000, 4_000_000),
    "Aurangzeb":              (4_600_000,  4000, 4_000_000),
    "Babur":                  (300_000,    10,   1_000_000),
    "Shivaji":                (100_000,    8,    100_000),
    "Tipu Sultan":            (100_000,    600,  50_000),
    "Chandragupta Maurya":    (500_000,    500,  5_000_000),
    "Shaka Zulu":             (2_000_000,  1200, 30_000),
    "Mansa Musa":             (50_000,     1000, 1_300_000),
    "Nabucodonosor II":       (200_000,    100,  500_000),
    "Ramses II":              (100_000,    100,  1_000_000),
    "Thutmose III":           (100_000,    50,   1_000_000),
    "Sargon di Akkad":        (100_000,    50,   800_000),
    "Hammurabi":              (50_000,     50,   300_000),
    "Leonida I":              (50_000,     3,    0),
    "Pirro":                  (150_000,    5,    100_000),
    "Silla":                  (500_000,    5,    0),
    "Gaio Mario":             (300_000,    4,    0),
    "Crasso":                 (200_000,    2,    0),
    "Pompeo":                 (500_000,    5,    0),
    "Marco Antonio":          (200_000,    4,    0),
    "Augusto":                (500_000,    3,    5_000_000),
    "Traiano":                (1_000_000,  2,    6_500_000),
    "Costantino il Grande":   (500_000,    3,    4_400_000),
    "Giustiniano I":          (500_000,    2,    3_500_000),
    "Basilio II":             (500_000,    1,    1_300_000),
    "Eraclio":                (400_000,    2,    2_000_000),
    "Nerone":                 (50_000,     6,    5_000_000),
    "Caligola":               (30_000,     10,   5_000_000),
    "Commodo":                (20_000,     300,  5_000_000),
    "Marco Aurelio":          (200_000,    1,    5_000_000),
    "Adriano":                (100_000,    2,    5_000_000),
    "Diocleziano":            (300_000,    1,    5_000_000),
    "Napoleone III":          (500_000,    12,   500_000),
    "Otto von Bismarck":      (500_000,    1,    540_000),
    "Guglielmo II":           (10_000_000, 2,    2_600_000),
    "Benito Mussolini":       (1_000_000,  30,   3_500_000),
    "Francisco Franco":       (500_000,    1,    500_000),
    "Hideki Tojo":            (5_000_000,  1,    7_400_000),
    "Erwin Rommel":           (100_000,    2,    0),
    "Georgij Zukov":          (500_000,    2,    0),
    "George Patton":          (100_000,    2,    0),
    "Erich Ludendorff":       (2_000_000,  2,    0),
    "Wellington":             (100_000,    2,    0),
    "Horatio Nelson":         (30_000,     3,    0),
    "Chiang Kai-shek":        (10_000_000, 4,    11_400_000),
    "Pol Pot":                (2_000_000,  2,    181_000),
    "Idi Amin":               (500_000,    30,   241_000),
    "Saddam Hussein":         (1_000_000,  4,    438_000),
    "Muammar Gheddafi":       (100_000,    5,    1_760_000),
    "Kim Il-sung":            (1_600_000,  3,    120_000),
    "Leopoldo II del Belgio": (10_000_000, 3,    2_345_000),
    "Cristoforo Colombo":     (100_000,    3,    0),
    "Hernan Cortes":          (500_000,    5,    2_000_000),
    "Francisco Pizarro":      (500_000,    4,    2_000_000),
    "Vasco da Gama":          (10_000,     2,    0),
    "Ferdinando Magellano":   (5_000,      2,    0),
    "Oda Nobunaga":           (200_000,    10,   250_000),
    "Toyotomi Hideyoshi":     (300_000,    16,   380_000),
    "Tokugawa Ieyasu":        (200_000,    20,   380_000),
    "Takeda Shingen":         (100_000,    5,    50_000),
    "Nader Shah":             (1_000_000,  100,  4_500_000),
    "Shah Abbas I":           (300_000,    300,  2_800_000),
    "Enrico VIII":            (72_000,     6,    250_000),
    "Elisabetta I":           (100_000,    0,    250_000),
    "Luigi XIV":              (1_500_000,  20,   1_000_000),
    "Filippo II di Spagna":   (2_000_000,  4,    31_000_000),
    "Carlo V":                (1_000_000,  2,    28_000_000),
    "Federico il Grande":     (500_000,    1,    195_000),
    "Federico Barbarossa":    (200_000,    3,    1_000_000),
    "Enrico V":               (100_000,    2,    250_000),
    "Edoardo I":              (100_000,    3,    150_000),
    "Riccardo III":           (30_000,     1,    150_000),
    "Vittoria del Regno Unito": (20_000_000, 1,  30_000_000),
    "Lenin":                  (5_000_000,  3,    22_400_000),
    "Vladimiro il Grande":    (100_000,    800,  1_300_000),
    "Aleksandr Nevskij":      (50_000,     1,    0),
    "Sundiata Keita":         (100_000,    100,  1_000_000),
    "Menelik II":             (100_000,    5,    1_100_000),
    "Haile Selassie":         (700_000,    1,    1_100_000),
    "Cetshwayo":              (50_000,     20,   30_000),
    "Samori Ture":            (100_000,    50,   300_000),
    "Mitridate VI":           (300_000,    20,   500_000),
    "Seleuco I":              (300_000,    3,    4_000_000),
    "Tolomeo I":              (200_000,    5,    1_500_000),
    "Antioco III":            (300_000,    5,    3_000_000),
    "Filippo II di Macedonia":(200_000,    7,    500_000),
    "Cambise II":             (200_000,    5,    5_500_000),
    "Sapore I":               (200_000,    5,    3_500_000),
    "Cosroe I":               (300_000,    100,  3_600_000),
    "Ardashir I":             (200_000,    50,   3_500_000),
    "Ismail I":               (200_000,    50,   2_800_000),
    "Ranjit Singh":           (100_000,    46,   520_000),
    "Prithviraj Chauhan":     (50_000,     13,   500_000),
}

# ---------------------------------------------------------------------------
# Definizione delle "scale" storiche: (kills, women, territory) intervalli
# ---------------------------------------------------------------------------
TIERS = {
    "legend":     ((3_000_000, 25_000_000), (200, 3000), (5_000_000, 20_000_000)),
    "conqueror":  ((500_000, 5_000_000),    (50, 800),   (1_500_000, 9_000_000)),
    "emperor":    ((80_000, 1_500_000),     (20, 400),   (600_000, 6_000_000)),
    "king":       ((15_000, 400_000),       (2, 30),     (80_000, 2_500_000)),
    "general":    ((30_000, 900_000),       (1, 12),     (0, 300_000)),
    "warlord":    ((80_000, 3_000_000),     (2, 60),     (10_000, 700_000)),
    "dictator":   ((300_000, 15_000_000),   (1, 25),     (100_000, 4_000_000)),
    "minor":      ((1_000, 60_000),         (1, 18),     (3_000, 250_000)),
    "explorer":   ((2_000, 250_000),        (1, 8),      (50_000, 3_000_000)),
    "sultan":     ((100_000, 1_500_000),    (50, 500),   (900_000, 4_500_000)),
}

def seeded(name, salt, lo, hi):
    """Numero deterministico in [lo, hi] a partire dal nome (distribuzione log)."""
    if hi <= lo:
        return lo
    h = hashlib.sha256(f"{name}|{salt}".encode()).hexdigest()
    frac = int(h[:12], 16) / float(16**12)
    # distribuzione logaritmica per valori piu' realistici (molti piccoli, pochi enormi)
    import math
    val = math.exp(math.log(lo + 1) + frac * (math.log(hi + 1) - math.log(lo + 1))) - 1
    return int(round(val))

def make(name, tier, era, emoji):
    (kr, wr, tr) = TIERS[tier]
    if name in FAMOUS:
        k, w, t = FAMOUS[name]
    else:
        k = seeded(name, "k", *kr)
        w = seeded(name, "w", *wr)
        t = seeded(name, "t", *tr)
    return {"name": name, "era": era, "emoji": emoji,
            "kills": k, "women": w, "territory": t}

# ---------------------------------------------------------------------------
# Liste di personaggi storici reali, per gruppo. (tier, era, emoji, [nomi])
# ---------------------------------------------------------------------------
GROUPS = [
 ("legend", "Antichità / Medioevo", "🐎", [
    "Gengis Khan","Tamerlano","Attila",
 ]),
 ("conqueror", "Antichità", "⚔️", [
    "Alessandro Magno","Giulio Cesare","Ciro il Grande","Dario I","Serse I",
    "Cambise II","Filippo II di Macedonia","Seleuco I","Tolomeo I","Antioco III",
    "Mitridate VI","Chandragupta Maurya","Ashoka","Qin Shi Huang","Sargon di Akkad",
    "Nabucodonosor II","Ramses II","Thutmose III","Sapore I","Cosroe I","Ardashir I",
 ]),
 ("conqueror", "Medioevo", "🛡️", [
    "Carlo Magno","Saladino","Federico Barbarossa","Guglielmo il Conquistatore",
    "Kublai Khan","Hulagu Khan","Batu Khan","Ogedei Khan","Mongke Khan","Guyuk Khan",
    "Babur","Akbar","Aurangzeb","Nader Shah","Shah Abbas I","Ismail I",
 ]),
 ("conqueror", "Età moderna", "🏰", [
    "Napoleone Bonaparte","Solimano il Magnifico","Maometto II","Selim I",
    "Ivan il Terribile","Pietro il Grande","Caterina la Grande","Carlo V",
    "Filippo II di Spagna","Luigi XIV","Federico il Grande",
 ]),
 ("dictator", "XX secolo", "💀", [
    "Adolf Hitler","Iosif Stalin","Mao Zedong","Benito Mussolini","Francisco Franco",
    "Hideki Tojo","Pol Pot","Idi Amin","Saddam Hussein","Muammar Gheddafi",
    "Kim Il-sung","Chiang Kai-shek","Leopoldo II del Belgio","Guglielmo II",
    "Lenin","Nicolae Ceausescu","Augusto Pinochet","Slobodan Milosevic",
    "Mengistu Haile Mariam","Kim Jong-il","Enver Hoxha","Josip Broz Tito",
    "Ho Chi Minh","Fidel Castro","Suharto","Ferdinand Marcos",
 ]),
 ("general", "Guerre napoleoniche / mondiali", "🎖️", [
    "Wellington","Horatio Nelson","Erwin Rommel","Georgij Zukov","George Patton",
    "Erich Ludendorff","Dwight Eisenhower","Douglas MacArthur","Bernard Montgomery",
    "Heinz Guderian","Konstantin Rokossovskij","Ivan Konev","Chester Nimitz",
    "Isoroku Yamamoto","Paul von Hindenburg","Ferdinand Foch","Douglas Haig",
    "Aleksei Brusilov","Michel Ney","Louis-Nicolas Davout","Andre Massena",
    "Gebhard von Blucher","Mikhail Kutuzov","Barclay de Tolly","Robert E. Lee",
    "Ulysses S. Grant","Stonewall Jackson","William Sherman","George Washington",
    "Winfield Scott","John Pershing","George Marshall","Omar Bradley",
    "Curtis LeMay","Vasilij Cujkov","Semyon Timosenko","Kliment Vorosilov",
 ]),
 ("emperor", "Imperatori romani", "🏛️", [
    "Augusto","Tiberio","Caligola","Claudio","Nerone","Galba","Otone","Vitellio",
    "Vespasiano","Tito","Domiziano","Nerva","Traiano","Adriano","Antonino Pio",
    "Marco Aurelio","Lucio Vero","Commodo","Pertinace","Didio Giuliano",
    "Settimio Severo","Caracalla","Geta","Macrino","Eliogabalo","Alessandro Severo",
    "Massimino il Trace","Gordiano I","Gordiano II","Pupieno","Balbino","Gordiano III",
    "Filippo l'Arabo","Decio","Treboniano Gallo","Emiliano","Valeriano","Gallieno",
    "Claudio il Gotico","Quintillo","Aureliano","Tacito","Floriano","Probo","Caro",
    "Carino","Numeriano","Diocleziano","Massimiano","Costanzo Cloro","Galerio",
    "Costantino il Grande","Licinio","Costantino II","Costante","Costanzo II",
    "Giuliano","Gioviano","Valentiniano I","Valente","Graziano","Valentiniano II",
    "Teodosio I","Arcadio","Onorio","Teodosio II","Valentiniano III",
 ]),
 ("emperor", "Imperatori bizantini", "☦️", [
    "Giustiniano I","Giustino I","Eraclio","Costante II","Costantino IV",
    "Giustiniano II","Leone III","Costantino V","Irene di Atene","Niceforo I",
    "Basilio I","Leone VI","Costantino VII","Romano I","Niceforo II Foca",
    "Giovanni I Zimisce","Basilio II","Costantino VIII","Romano III","Michele IV",
    "Costantino IX","Teodora","Isacco I Comneno","Costantino X","Romano IV",
    "Alessio I Comneno","Giovanni II Comneno","Manuele I Comneno","Andronico I Comneno",
    "Isacco II Angelo","Alessio III Angelo","Michele VIII Paleologo","Andronico II",
    "Giovanni VI Cantacuzeno","Manuele II Paleologo","Costantino XI Paleologo",
 ]),
 ("sultan", "Sultani ottomani", "🌙", [
    "Osman I","Orhan","Murad I","Bayezid I","Mehmed I","Murad II","Bayezid II",
    "Selim II","Murad III","Mehmed III","Ahmed I","Mustafa I","Osman II","Murad IV",
    "Ibrahim I","Mehmed IV","Suleiman II","Ahmed II","Mustafa II","Ahmed III",
    "Mahmud I","Osman III","Mustafa III","Abdul Hamid I","Selim III","Mustafa IV",
    "Mahmud II","Abdulmecid I","Abdulaziz","Murad V","Abdul Hamid II","Mehmed V","Mehmed VI",
 ]),
 ("emperor", "Imperatori cinesi", "🐉", [
    "Han Gaozu","Imperatore Wen di Han","Imperatore Jing di Han","Imperatore Wu di Han",
    "Wang Mang","Guangwu","Imperatore Ming di Han","Imperatore Zhang di Han",
    "Cao Cao","Liu Bei","Sun Quan","Sima Yan","Fu Jian","Imperatore Wen di Sui",
    "Imperatore Yang di Sui","Imperatore Gaozu di Tang","Imperatore Taizong di Tang",
    "Wu Zetian","Imperatore Xuanzong di Tang","Imperatore Taizu di Song",
    "Imperatore Zhenzong","Imperatore Huizong","Hongwu","Yongle","Imperatore Jiajing",
    "Imperatore Wanli","Imperatore Chongzhen","Nurhaci","Huang Taiji","Imperatore Shunzhi",
    "Kangxi","Yongzheng","Qianlong","Imperatore Jiaqing","Imperatore Daoguang",
    "Imperatore Xianfeng","Imperatore Guangxu","Puyi","Cixi",
 ]),
 ("king", "Re d'Inghilterra", "👑", [
    "Guglielmo II d'Inghilterra","Enrico I d'Inghilterra","Stefano d'Inghilterra",
    "Enrico II d'Inghilterra","Riccardo Cuor di Leone","Giovanni Senzaterra",
    "Enrico III d'Inghilterra","Edoardo I","Edoardo II","Edoardo III","Riccardo II",
    "Enrico IV d'Inghilterra","Enrico V","Enrico VI","Edoardo IV","Riccardo III",
    "Enrico VII","Enrico VIII","Edoardo VI","Maria I d'Inghilterra","Elisabetta I",
    "Giacomo I d'Inghilterra","Carlo I d'Inghilterra","Carlo II d'Inghilterra",
    "Giacomo II d'Inghilterra","Guglielmo III d'Inghilterra","Anna di Gran Bretagna",
    "Giorgio I","Giorgio II","Giorgio III","Giorgio IV","Guglielmo IV",
    "Vittoria del Regno Unito","Edoardo VII","Giorgio V","Giorgio VI",
 ]),
 ("king", "Re di Francia", "⚜️", [
    "Ugo Capeto","Roberto II di Francia","Enrico I di Francia","Filippo I di Francia",
    "Luigi VI di Francia","Luigi VII di Francia","Filippo II Augusto","Luigi VIII",
    "Luigi IX di Francia","Filippo III di Francia","Filippo IV il Bello","Luigi X",
    "Filippo V di Francia","Carlo IV di Francia","Filippo VI di Francia","Giovanni II",
    "Carlo V di Francia","Carlo VI di Francia","Carlo VII di Francia","Luigi XI",
    "Carlo VIII di Francia","Luigi XII","Francesco I di Francia","Enrico II di Francia",
    "Francesco II di Francia","Carlo IX di Francia","Enrico III di Francia","Enrico IV di Francia",
    "Luigi XIII","Luigi XV","Luigi XVI","Napoleone III","Luigi XVIII","Carlo X di Francia",
    "Luigi Filippo I",
 ]),
 ("king", "Re di Spagna / Iberia", "🏵️", [
    "Ferdinando II d'Aragona","Isabella I di Castiglia","Filippo III di Spagna",
    "Filippo IV di Spagna","Carlo II di Spagna","Filippo V di Spagna","Ferdinando VI",
    "Carlo III di Spagna","Carlo IV di Spagna","Ferdinando VII","Isabella II di Spagna",
    "Alfonso XII","Alfonso XIII","Giovanni I del Portogallo","Manuele I del Portogallo",
    "Giovanni II del Portogallo","Alfonso Henriques","Pietro I del Portogallo",
 ]),
 ("warlord", "Condottieri e signori della guerra", "🗡️", [
    "Vlad l'Impalatore","Stefano il Grande","Giovanni Hunyadi","El Cid",
    "Bertrand du Guesclin","Jan Zizka","Skanderbeg","Ezzelino III da Romano",
    "Francesco Sforza","Cesare Borgia","Bartolomeo Colleoni","Federico da Montefeltro",
    "Gian Giacomo Trivulzio","Gonzalo de Cordoba","Il Duca di Alba","Alessandro Farnese",
    "Wallenstein","Gustavo Adolfo di Svezia","Carlo XII di Svezia","Maurizio di Sassonia",
    "Il Principe Eugenio","Marlborough","Turenne","Il Gran Conde","Yue Fei","Cao Cao",
 ]),
 ("warlord", "Guerrieri del Giappone feudale", "🎌", [
    "Oda Nobunaga","Toyotomi Hideyoshi","Tokugawa Ieyasu","Takeda Shingen",
    "Uesugi Kenshin","Date Masamune","Mori Motonari","Hojo Soun","Imagawa Yoshimoto",
    "Minamoto no Yoritomo","Minamoto no Yoshitsune","Taira no Kiyomori","Ashikaga Takauji",
    "Kusunoki Masashige","Sanada Yukimura","Honda Tadakatsu","Ii Naomasa",
    "Shimazu Yoshihiro","Chosokabe Motochika","Maeda Toshiie",
 ]),
 ("explorer", "Esploratori e conquistadores", "🧭", [
    "Cristoforo Colombo","Vasco da Gama","Ferdinando Magellano","Hernan Cortes",
    "Francisco Pizarro","Afonso de Albuquerque","Pedro de Alvarado","Diego de Almagro",
    "Vasco Nunez de Balboa","Francisco de Orellana","Juan Ponce de Leon",
    "Hernando de Soto","Francisco Vazquez de Coronado","Bartolomeu Dias",
    "Amerigo Vespucci","Giovanni Caboto","Jacques Cartier","Francis Drake",
    "Walter Raleigh","James Cook","Abel Tasman","Willem Barentsz",
 ]),
 ("king", "Zar e sovrani di Russia", "🐻", [
    "Rurik","Vladimiro il Grande","Jaroslav il Saggio","Aleksandr Nevskij",
    "Ivan III di Russia","Vasilij III di Russia","Boris Godunov","Michele di Russia",
    "Alessio I di Russia","Elisabetta di Russia","Paolo I di Russia","Alessandro I di Russia",
    "Nicola I di Russia","Alessandro II di Russia","Alessandro III di Russia","Nicola II di Russia",
 ]),
 ("emperor", "Sovrani dell'India", "🕉️", [
    "Humayun","Shah Jahan","Jahangir","Shivaji","Tipu Sultan","Ranjit Singh",
    "Prithviraj Chauhan","Krishnadevaraya","Rana Pratap","Hyder Ali","Bajirao I",
    "Samudragupta","Harsha","Rajaraja I","Rajendra Chola I","Pulakesin II","Kanishka",
 ]),
 ("king", "Sovrani d'Africa", "🦁", [
    "Mansa Musa","Sundiata Keita","Menelik II","Haile Selassie","Cetshwayo",
    "Samori Ture","Shaka Zulu","Dingane","Tewodros II","Yohannes IV","Behanzin",
    "Sonni Ali","Askia Muhammad I","Idris Alooma","Ramanantsoa","Ranavalona I",
    "Osei Tutu","Moshoeshoe I","Lobengula","Mutota",
 ]),
 ("king", "Sovrani persiani e mediorientali", "🏺", [
    "Ismail I","Abbas II di Persia","Karim Khan Zand","Agha Mohammad Khan",
    "Fath Ali Shah","Naser al-Din Shah","Reza Pahlavi","Harun al-Rashid",
    "Al-Mansur","Al-Ma'mun","Al-Mu'tasim","Mu'awiya I","Abd al-Malik","Umar",
    "Khalid ibn al-Walid","Tariq ibn Ziyad","Baibars","Qutuz","Timur Lang",
 ]),
 ("general", "Antichità classica", "🏹", [
    "Annibale","Scipione l'Africano","Silla","Gaio Mario","Crasso","Pompeo",
    "Marco Antonio","Leonida I","Pirro","Temistocle","Milziade","Pausania",
    "Lisandro","Epaminonda","Cimone","Alcibiade","Brasida","Fabio Massimo",
    "Marcello","Emilio Paolo","Germanico","Agricola","Belisario","Narsete",
    "Flavio Ezio","Stilicone","Vercingetorige","Arminio","Spartaco","Boudicca",
 ]),
]

# ---------------------------------------------------------------------------
# Costruzione dataset
# ---------------------------------------------------------------------------
people = []
seen = set()
for tier, era, emoji, names in GROUPS:
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        people.append(make(n, tier, era, emoji))

# --- Espansione con dinastie reali per superare i 1000 personaggi ---------
# Generatori parametrici di sovrani reali (nomi + numeri regnanti realmente esistiti)
EXPANSION = [
 ("king", "Sacro Romano Impero", "🦅", "Ottone", 1, 4, "il Grande"),
 ("king", "Sacro Romano Impero", "🦅", "Enrico", 1, 7, "di Germania"),
 ("king", "Sacro Romano Impero", "🦅", "Corrado", 1, 4, "di Germania"),
 ("king", "Sacro Romano Impero", "🦅", "Federico", 1, 3, "di Svevia"),
 ("king", "Sacro Romano Impero", "🦅", "Massimiliano", 1, 2, "d'Asburgo"),
 ("king", "Sacro Romano Impero", "🦅", "Ferdinando", 1, 3, "d'Asburgo"),
 ("king", "Sacro Romano Impero", "🦅", "Leopoldo", 1, 2, "d'Asburgo"),
 ("king", "Sacro Romano Impero", "🦅", "Giuseppe", 1, 2, "d'Asburgo"),
 ("king", "Regno di Napoli", "🌋", "Ferdinando", 1, 4, "di Napoli"),
 ("king", "Regno di Sicilia", "🌋", "Ruggero", 1, 2, "di Sicilia"),
 ("king", "Regno di Sicilia", "🌋", "Guglielmo", 1, 2, "di Sicilia"),
 ("king", "Regno di Scozia", "🏴", "Giacomo", 1, 5, "di Scozia"),
 ("king", "Regno di Scozia", "🏴", "Alessandro", 1, 3, "di Scozia"),
 ("king", "Regno di Danimarca", "❄️", "Cristiano", 1, 10, "di Danimarca"),
 ("king", "Regno di Danimarca", "❄️", "Federico", 1, 9, "di Danimarca"),
 ("king", "Regno di Svezia", "❄️", "Gustavo", 1, 6, "di Svezia"),
 ("king", "Regno di Svezia", "❄️", "Carlo", 9, 16, "di Svezia"),
 ("king", "Regno di Norvegia", "❄️", "Haakon", 1, 7, "di Norvegia"),
 ("king", "Regno di Norvegia", "❄️", "Olaf", 1, 5, "di Norvegia"),
 ("king", "Regno di Polonia", "🦬", "Boleslao", 1, 5, "di Polonia"),
 ("king", "Regno di Polonia", "🦬", "Casimiro", 1, 4, "di Polonia"),
 ("king", "Regno di Polonia", "🦬", "Ladislao", 1, 4, "di Polonia"),
 ("king", "Regno d'Ungheria", "🐎", "Bela", 1, 4, "d'Ungheria"),
 ("king", "Regno d'Ungheria", "🐎", "Ladislao", 1, 5, "d'Ungheria"),
 ("king", "Regno d'Ungheria", "🐎", "Stefano", 1, 5, "d'Ungheria"),
 ("king", "Regno del Portogallo", "🏵️", "Alfonso", 1, 6, "del Portogallo"),
 ("king", "Regno del Portogallo", "🏵️", "Giovanni", 3, 6, "del Portogallo"),
 ("king", "Regno d'Aragona", "🏵️", "Pietro", 1, 4, "d'Aragona"),
 ("king", "Regno d'Aragona", "🏵️", "Alfonso", 1, 5, "d'Aragona"),
 ("king", "Regno d'Aragona", "🏵️", "Giacomo", 1, 2, "d'Aragona"),
 ("king", "Regno di Castiglia", "🏵️", "Alfonso", 6, 11, "di Castiglia"),
 ("king", "Regno di Castiglia", "🏵️", "Enrico", 1, 4, "di Castiglia"),
 ("king", "Regno di Castiglia", "🏵️", "Sancho", 1, 4, "di Castiglia"),
 ("king", "Regno di Boemia", "🦁", "Venceslao", 1, 4, "di Boemia"),
 ("king", "Regno di Boemia", "🦁", "Ottocaro", 1, 2, "di Boemia"),
 ("emperor", "Dinastia Achemenide", "🏺", "Artaserse", 1, 3, "di Persia"),
 ("emperor", "Dinastia Tolemaica", "🏺", "Tolomeo", 2, 12, "d'Egitto"),
 ("emperor", "Dinastia Seleucide", "🏺", "Antioco", 4, 13, "il Seleucide"),
 ("emperor", "Dinastia Seleucide", "🏺", "Seleuco", 2, 6, "il Seleucide"),
 ("king", "Faraoni d'Egitto", "𓂀", "Ramses", 3, 11, "d'Egitto"),
 ("king", "Faraoni d'Egitto", "𓂀", "Thutmose", 1, 2, "d'Egitto"),
 ("king", "Faraoni d'Egitto", "𓂀", "Amenhotep", 1, 4, "d'Egitto"),
 ("king", "Faraoni d'Egitto", "𓂀", "Psammetico", 1, 3, "d'Egitto"),
 ("emperor", "Impero del Giappone", "🎎", "Imperatore Go-", 1, 1, "Daigo"),
 ("king", "Regni greci ellenistici", "🏛️", "Demetrio", 1, 3, "di Macedonia"),
 ("king", "Regni greci ellenistici", "🏛️", "Antigono", 1, 3, "di Macedonia"),
 ("king", "Regno di Numidia", "🏜️", "Giuba", 1, 2, "di Numidia"),
 ("king", "Regno del Ponto", "🏔️", "Farnace", 1, 2, "del Ponto"),
 ("king", "Regno di Pergamo", "🏛️", "Attalo", 1, 3, "di Pergamo"),
 ("king", "Regno d'Armenia", "🏔️", "Tigrane", 1, 2, "d'Armenia"),
 ("king", "Regno di Gerusalemme", "✝️", "Baldovino", 1, 5, "di Gerusalemme"),
 ("king", "Impero latino", "✝️", "Roberto", 1, 1, "di Courtenay"),
 ("king", "Regno di Cipro", "✝️", "Ugo", 1, 4, "di Lusignano"),
 ("king", "Regno di Baviera", "🍺", "Ludovico", 1, 3, "di Baviera"),
 ("king", "Regno di Baviera", "🍺", "Massimiliano", 1, 2, "di Baviera"),
 ("king", "Regno di Prussia", "🦅", "Federico Guglielmo", 1, 4, "di Prussia"),
 ("king", "Regno di Prussia", "🦅", "Guglielmo", 1, 2, "di Prussia"),
 ("king", "Regno d'Italia", "🇮🇹", "Vittorio Emanuele", 1, 3, "d'Italia"),
 ("king", "Regno d'Italia", "🇮🇹", "Umberto", 1, 2, "d'Italia"),
 ("king", "Regno dei Paesi Bassi", "🌷", "Guglielmo", 1, 3, "dei Paesi Bassi"),
 ("king", "Regno del Belgio", "🇧🇪", "Alberto", 1, 2, "del Belgio"),
 ("king", "Regno di Grecia", "🏛️", "Giorgio", 1, 2, "di Grecia"),
 ("king", "Regno di Grecia", "🏛️", "Costantino", 1, 2, "di Grecia"),
 ("king", "Regno di Romania", "🦇", "Carol", 1, 2, "di Romania"),
 ("king", "Regno di Serbia", "🦅", "Milan", 1, 1, "di Serbia"),
 ("king", "Regno di Serbia", "🦅", "Stefano", 1, 5, "Nemanjic"),
 ("king", "Regno di Bulgaria", "🦁", "Boris", 1, 3, "di Bulgaria"),
 ("king", "Regno di Bulgaria", "🦁", "Simeone", 1, 2, "di Bulgaria"),
 ("king", "Impero bulgaro", "🦁", "Ivan", 1, 3, "Asen"),
 ("king", "Regno di Scozia", "🏴", "Roberto", 1, 3, "di Scozia"),
 ("king", "Regno di Scozia", "🏴", "Davide", 1, 2, "di Scozia"),
 ("king", "Regno d'Irlanda", "🍀", "Brian", 1, 1, "Boru"),
 ("king", "Regni anglosassoni", "⚔️", "Etelredo", 1, 2, "d'Inghilterra"),
 ("king", "Regni anglosassoni", "⚔️", "Edmondo", 1, 2, "d'Inghilterra"),
 ("king", "Regni anglosassoni", "⚔️", "Edoardo", 1, 3, "il Vecchio"),
 ("king", "Casato di Valois", "⚜️", "Filippo", 1, 3, "di Borgogna"),
 ("emperor", "Dinastia Han", "🐉", "Imperatore An di", 1, 1, "Han"),
 ("emperor", "Dinastia Ming", "🐉", "Imperatore Zhengde di", 1, 1, "Ming"),
 ("emperor", "Dinastia Song", "🐉", "Imperatore Renzong di", 1, 1, "Song"),
 ("emperor", "Dinastia Jin", "🐉", "Imperatore Shizong di", 1, 1, "Jin"),
 ("king", "Regno di Georgia", "🏔️", "Davide", 1, 4, "di Georgia"),
 ("king", "Regno di Georgia", "🏔️", "Giorgio", 1, 3, "di Georgia"),
 ("king", "Regno d'Armenia", "🏔️", "Ashot", 1, 3, "d'Armenia"),
 ("king", "Dinastia coreana Joseon", "🏯", "Re Sejong", 1, 1, "il Grande"),
 ("king", "Regno di Goguryeo", "🏯", "Re Gwanggaeto", 1, 1, "il Grande"),
 ("king", "Sovrani del Siam", "🐘", "Rama", 1, 9, "del Siam"),
 ("king", "Impero Khmer", "🛕", "Jayavarman", 1, 7, "Khmer"),
 ("king", "Impero Vijayanagara", "🕉️", "Deva Raya", 1, 2, "Vijayanagara"),
 ("king", "Dinastia Chola", "🕉️", "Kulothunga", 1, 3, "Chola"),
 ("emperor", "Dinastia Gupta", "🕉️", "Chandragupta", 1, 2, "Gupta"),
 ("emperor", "Dinastia Maurya", "🕉️", "Bindusara", 1, 1, "Maurya"),
 ("sultan", "Sultanato di Delhi", "🌙", "Alauddin", 1, 1, "Khalji"),
 ("sultan", "Sultanato di Delhi", "🌙", "Muhammad", 1, 1, "bin Tughluq"),
 ("sultan", "Sultanato mamelucco", "🌙", "Baibars", 1, 1, "il Mamelucco"),
 ("sultan", "Dinastia ayyubide", "🌙", "Al-Adil", 1, 2, "l'Ayyubide"),
 ("sultan", "Impero songhai", "🦁", "Askia", 1, 1, "Daoud"),
 ("king", "Impero azteco", "🌵", "Montezuma", 1, 2, "azteco"),
 ("king", "Impero azteco", "🌵", "Axayacatl", 1, 1, "azteco"),
 ("king", "Impero inca", "🏔️", "Pachacutec", 1, 1, "inca"),
 ("king", "Impero inca", "🏔️", "Huayna", 1, 1, "Capac"),
 ("king", "Impero inca", "🏔️", "Atahualpa", 1, 1, "inca"),
 ("warlord", "Regni vichinghi", "⚓", "Harald", 1, 3, "di Norvegia"),
 ("warlord", "Regni vichinghi", "⚓", "Canuto", 1, 2, "il Grande"),
 ("warlord", "Regni vichinghi", "⚓", "Sweyn", 1, 2, "Barbaforcuta"),
 ("king", "Rus' di Kiev", "🐻", "Svjatoslav", 1, 2, "di Kiev"),
 ("king", "Rus' di Kiev", "🐻", "Mstislav", 1, 2, "di Kiev"),
 ("king", "Granducato di Lituania", "🦬", "Vitoldo", 1, 1, "di Lituania"),
 ("king", "Granducato di Lituania", "🦬", "Gediminas", 1, 1, "di Lituania"),
 ("dictator", "Leader del XX secolo", "💀", "Kim", 2, 3, "Jong-un"),
]

# Liste piatte aggiuntive di figure storiche reali
FLAT = [
 ("general", "Rivoluzioni e indipendenze", "🎖️", [
    "Simon Bolivar","Jose de San Martin","Bernardo O'Higgins","Antonio Jose de Sucre",
    "Miguel Hidalgo","Jose Maria Morelos","Emiliano Zapata","Pancho Villa",
    "Giuseppe Garibaldi","Lajos Kossuth","Tadeusz Kosciuszko","Michele il Bravo",
    "Toussaint Louverture","Jean-Jacques Dessalines","Sam Houston","Nathanael Greene",
 ]),
 ("dictator", "Conflitti moderni", "💀", [
    "Francisco Solano Lopez","Rafael Trujillo","Anastasio Somoza","Jean-Bedel Bokassa",
    "Hissene Habre","Charles Taylor","Foday Sankoh","Laurent Kabila","Mobutu Sese Seko",
    "Sani Abacha","Omar al-Bashir","Hafez al-Assad","Bashar al-Assad","Ruhollah Khomeini",
    "Ayatollah Ali Khamenei","Than Shwe","Ne Win","Nursultan Nazarbayev","Islam Karimov",
    "Saparmurat Niyazov","Alexander Lukashenko","Robert Mugabe","Kwame Nkrumah",
 ]),
 ("general", "Comandanti del XX secolo", "🎖️", [
    "Ataturk","Josip Broz Tito","Vo Nguyen Giap","Zhu De","Lin Biao","Peng Dehuai",
    "Douglas MacArthur","William Slim","Claude Auchinleck","Archibald Wavell",
    "Albert Kesselring","Gerd von Rundstedt","Walther Model","Karl Donitz",
    "Hermann Goring","Wilhelm Keitel","Alfred Jodl","Friedrich Paulus",
    "Mannerheim","Ion Antonescu","Miklos Horthy","Francisco Macias Nguema",
    "Moshe Dayan","Ariel Sharon","Yitzhak Rabin","Norman Schwarzkopf","Colin Powell",
 ]),
 ("warlord", "Pirati e corsari", "🏴‍☠️", [
    "Barbanera","Henry Morgan","Bartholomew Roberts","Calico Jack","Zheng Yi Sao",
    "Barbarossa","Dragut","Jean Bart","Francois l'Olonnais","Henry Every",
    "William Kidd","Stede Bonnet","Klaus Stortebeker","Kanhoji Angre",
 ]),
 ("king", "Altri sovrani europei", "👑", [
    "Matthias Corvino","Vladislao II di Boemia","Luigi II d'Ungheria","Sigismondo di Lussemburgo",
    "Alberto II d'Asburgo","Rodolfo I d'Asburgo","Wenceslao IV di Boemia","Ottone IV di Brunswick",
    "Filippo di Svevia","Corrado IV di Svevia","Manfredi di Sicilia","Carlo I d'Angio",
    "Carlo II d'Angio","Roberto d'Angio","Ladislao di Napoli","Giovanna I di Napoli",
    "Alfonso il Magnanimo","Renato d'Angio","Ferrante di Napoli","Federico di Napoli",
    "Cosimo de' Medici","Lorenzo de' Medici","Ludovico Sforza","Gian Galeazzo Visconti",
    "Cangrande della Scala","Francesco Petrarca il Vecchio","Andrea Doria","Sebastiano Venier",
 ]),
 ("emperor", "Ultimi imperatori e monarchi", "👑", [
    "Francesco Giuseppe I","Carlo I d'Austria","Guglielmo I di Germania","Federico III di Germania",
    "Meiji","Taisho","Hirohito","Bao Dai","Norodom Sihanouk","Rama V",
    "Fuad I d'Egitto","Faruq d'Egitto","Faysal I dell'Iraq","Abd Allah I di Giordania",
    "Ibn Saud","Mohammed Zahir Shah","Gustavo V di Svezia","Cristiano X di Danimarca",
    "Haakon VII di Norvegia","Guglielmina dei Paesi Bassi","Leopoldo III del Belgio",
 ]),
]

for tier, era, emoji, base, start, end, suffix in EXPANSION:
    roman = ["","I","II","III","IV","V","VI","VII","VIII","IX","X",
             "XI","XII","XIII","XIV","XV","XVI"]
    for i in range(start, end + 1):
        if base.endswith("-"):
            name = f"{base}{suffix}" if i == start else f"{base}{suffix} {roman[i]}"
        else:
            name = f"{base} {roman[i]} {suffix}".strip()
        if name in seen:
            continue
        seen.add(name)
        people.append(make(name, tier, era, emoji))

for tier, era, emoji, names in FLAT:
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        people.append(make(n, tier, era, emoji))

# Ordina alfabeticamente per pulizia (l'ordine non conta per il gioco)
people.sort(key=lambda p: p["name"])

print(f"Totale personaggi: {len(people)}")

out = "// Dataset generato automaticamente da tools/generate_data.py\n"
out += "// Valori approssimativi e a scopo puramente ludico.\n"
out += "window.CHARACTERS = " + json.dumps(people, ensure_ascii=False, indent=0) + ";\n"

with open("data.js", "w", encoding="utf-8") as f:
    f.write(out)
print("Scritto data.js")
