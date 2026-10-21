import os
import sys
import json
import base64
import asyncio
import edge_tts

VOICE = "ar-SA-HamedNeural"
RATE = "-10%"

# Fallback articles if no GEMINI_API_KEY is configured
FALLBACK_ARTICLES = [
    {
        "id": 1,
        "theme": "Business & Entrepreneuriat",
        "theme_ar": "الأَعْمَالُ وَرِيَادَةُ الأَعْمَالِ",
        "icon": "💼",
        "text": "يَبْدَأُ الْكَثِيرُ مِنَ الشَّبَابِ مَشَارِيعَ جَدِيدَةً كُلَّ عَامٍ. تُسَاعِدُ الشَّرِكَاتُ النَّاشِئَةُ فِي حَلِّ مَشَاكِلِ النَّاسِ الْيَوْمِيَّةِ، مِثْلَ شِرَاءِ الْمُنْتَجَاتِ عَبْرَ الْإِنْتِرْنِت. يَبْحَثُ أَصْحَابُ هَذِهِ الْمَشَارِيعِ عَنِ الْمَالِ لِتَكْبِيرِ أَعْمَالِهِمْ وَتَوْظِيفِ عُمَّالٍ جُدُدٍ.",
        "traduction": "De nombreux jeunes lancent de nouveaux projets chaque année. Les startups aident à résoudre les problèmes quotidiens des gens, comme l'achat de produits sur Internet. Les créateurs de ces projets recherchent des financements pour faire grandir leurs affaires et embaucher de nouveaux employés.",
        "vocab": [
            ("مَشَارِيعُ جَدِيدَةٌ", "mashārī' jadīdah", "nouveaux projets (singulier : mashrū')"),
            ("الشَّرِكَاتُ النَّاشِئَةُ", "ash-sharikāt an-nāshi'ah", "les jeunes pousses / startups"),
            ("شِرَاءُ الْمُنْتَجَاتِ", "shirā' al-muntajāt", "l'achat de produits"),
            ("تَوْظِيفُ عُمَّالٍ", "tawzīf 'ummāl", "l'embauche d'employés")
        ]
    },
    {
        "id": 2,
        "theme": "Géopolitique",
        "theme_ar": "الْجِيُوسِيَاسَةُ وَالْعَلَاقَاتُ الدَّوْلِيَّةُ",
        "icon": "🌍",
        "text": "تَتَعَاوَنُ الدُّوَلُ مَعًا لِتَحْقِيقِ السَّلَامِ وَالْأَمْنِ فِي الْعَالَمِ. تَلْتَقِي الْحُكُومَاتُ لِمُنَاقَشَةِ مَشَاكِلِ الِاقْتِصَادِ، وَتَبَادُلِ الْبَضَائِعِ وَالْأَغْذِيَةِ. يُسَاعِدُ هَذَا التَّعَاوُنُ الدَّوْلِيُّ عَلَى تَجَنُّبِ الْحُرُوبِ وَمُسَاعَدَةِ الشُّعُوبِ الْمُحْتَاجَةِ.",
        "traduction": "Les pays coopèrent ensemble pour instaurer la paix et la sécurité dans le monde. Les gouvernements se réunissent pour discuter des défis économiques et échanger des marchandises et de la nourriture. Cette coopération internationale permet d'éviter les guerres et de venir en aide aux populations dans le besoin.",
        "vocab": [
            ("تَتَعَاوَنُ الدُّوَلُ", "tata'āwanu ad-duwal", "les pays coopèrent"),
            ("تَحْقِيقُ السَّلَامِ", "tahqīq as-salām", "l'instauration de la paix"),
            ("تَبَادُلُ الْبَضَائِعِ", "tabādulu l-badā'i'", "l'échange de marchandises"),
            ("تَجَنُّبُ الْحُرُوبِ", "tajannubu l-hurūb", "éviter les guerres")
        ]
    },
    {
        "id": 3,
        "theme": "Informatique",
        "theme_ar": "الْمَعْلُومَاتِيَّةُ وَالْبَرْمَجَةُ",
        "icon": "💻",
        "text": "أَصْبَحَتْ لُغَاتُ الْبَرْمَجَةِ مَهَارَةً مُهِمَّةً لِلْحُصُولِ عَلَى وَظِيفَةٍ جَيِّدَةٍ. يَتَعَلَّمُ الطُّلَّابُ كَيْفِيَّةَ صِنَاعَةِ الْمَوَاقِعِ وَالتَّطْبِيقَاتِ لِلْهَوَاتِفِ الذَّكِيَّةِ. كَمَا يَهْتَمُّ الْمُهَنْدِسُونَ بِحِمَايَةِ الْحَوَاسِيبِ مِنَ الْفَيْرُوسَاتِ وَالسَّرِقَةِ الرَّقْمِيَّةِ.",
        "traduction": "Les langages de programmation sont devenus une compétence essentielle pour décrocher un bon emploi. Les étudiants apprennent comment créer des sites web et des applications pour smartphones. De même, les ingénieurs veillent à protéger les ordinateurs contre les virus et le piratage numérique.",
        "vocab": [
            ("لُغَاتُ الْبَرْمَجَةِ", "lughāt al-barmajah", "les langages de programmation"),
            ("وَظِيفَةٌ جَيِّدَةٌ", "wazīfatun jayyidah", "un bon emploi"),
            ("الْهَوَاتِفُ الذَّكِيَّةُ", "al-hawātifu dh-dhakiyyah", "les smartphones"),
            ("السَّرِقَةُ الرَّقْمِيَّةُ", "as-sariqatu r-raqamiyyah", "le piratage numérique")
        ]
    },
    {
        "id": 4,
        "theme": "Systèmes d'Information",
        "theme_ar": "نُظُمُ الْمَعْلُومَاتِ",
        "icon": "🗄️",
        "text": "تَسْتَخْدِمُ الشَّرِكَاتُ أَنْظِمَةَ الْحَاسُوبِ لِحِفْظِ مَعْلُومَاتِ الزَّبَائِنِ وَالْمَبِيعَاتِ. تُسَاعِدُ هَذِهِ النُّظُمُ الْمُدِيرَ عَلَى مَعْرِفَةِ أَرْبَاحِ الشَّرِكَةِ فِي أَيِّ وَقْتٍ. عِنْدَمَا تَكُونُ الْمَعْلُومَاتُ مُنَظَّمَةً، يَعْمَلُ الْمُوَظَّفُونَ بِسُرْعَةٍ وَدِقَّةٍ أَكْبَرَ.",
        "traduction": "Les entreprises utilisent des systèmes informatiques pour conserver les données des clients et les ventes. Ces systèmes aident le responsable à connaître les bénéfices de la société à tout moment. Lorsque les informations sont bien organisées, les employés travaillent avec plus de rapidité et de précision.",
        "vocab": [
            ("أَنْظِمَةُ الْحَاسُوبِ", "anzimatu l-hāsūb", "systèmes informatiques"),
            ("مَعْلُومَاتُ الزَّبَائِنِ", "ma'lūmātu z-zabā'in", "données clients"),
            ("أَرْبَاحُ الشَّرِكَةِ", "arbāhu sh-sharikah", "les bénéfices de l'entreprise"),
            ("مُوَظَّفُونَ", "muwazzafūn", "les employés")
        ]
    },
    {
        "id": 5,
        "theme": "Intelligence Artificielle",
        "theme_ar": "الذَّكَاءُ الِاصْطِنَاعِيُّ",
        "icon": "🤖",
        "text": "يُسَاعِدُ الذَّكَاءُ الِاصْطِنَاعِيُّ النَّاسَ فِي مَهَامِّهِمْ كُلَّ يَوْمٍ. يُمْكِنُ لِهَذِهِ الْبَرَامِجِ كِتَابَةُ الرَّسَائِلِ، وَتَرْجَمَةُ اللُّغَاتِ، وَالْإِجَابَةُ عَنِ الْأَسْئِلَةِ الصَّعْبَةِ. لَكِنْ يَبْقَى عَقْلُ الْإِنْسَانِ دَائِمًا هُوَ الْأَهَمَّ لِاتِّخَاذِ الْقَرَارَاتِ الصَّحِيحَةِ.",
        "traduction": "L'intelligence artificielle aide les gens dans leurs tâches au quotidien. Ces logiciels sont capables de rédiger des messages, de traduire des langues et de répondre à des questions complexes. Cependant, l'esprit humain reste toujours le plus important pour prendre les bonnes décisions.",
        "vocab": [
            ("مَهَامّ", "mahāmm", "tâches / missions"),
            ("تَرْجَمَةُ اللُّغَاتِ", "tarjamatu l-lughāt", "la traduction des langues"),
            ("عَقْلُ الْإِنْسَانِ", "'aqlu l-insān", "l'esprit humain"),
            ("اتِّخَاذُ الْقَرَارَاتِ", "ittikhādu l-qarārāt", "la prise de décisions")
        ]
    }
]

def fetch_articles():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY found, using default curriculum articles.")
        return FALLBACK_ARTICLES
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = """
Tu es un professeur d'arabe pour francophones. Génère 5 courts paragraphes d'actualités éducatives pour un apprenant de niveau Débutant (A2).
Les 5 thèmes :
1. Business & Entrepreneuriat (الأَعْمَالُ وَرِيَادَةُ الأَعْمَالِ)
2. Géopolitique (الْجِيُوسِيَاسَةُ وَالْعَلَاقَاتُ الدَّوْلِيَّةُ)
3. Informatique (الْمَعْلُومَاتِيَّةُ وَالْبَرْمَجَةُ)
4. Systèmes d'information (نُظُمُ الْمَعْلُومَاتِ)
5. Intelligence Artificielle (الذَّكَاءُ الِاصْطِنَاعِيُّ)

Règles impératives :
- Arabe accessible A2, phrases courtes, grammaire directe.
- VOYELLES COMPLÈTES (TASHKĪL) sur TOUS les mots arabes.
- Traduction française fluide.
- 4 mots de vocabulaire clé avec translittération phonétique et traduction.

Réponds STRICTEMENT sous forme de JSON valide (une liste de 5 objets) :
[
  {
    "id": 1,
    "theme": "Business & Entrepreneuriat",
    "theme_ar": "الأَعْمَالُ وَرِيَادَةُ الأَعْمَالِ",
    "icon": "💼",
    "text": "Texte arabe entièrement vocalisé",
    "traduction": "Traduction française",
    "vocab": [
      ["mot arabe vocalisé", "phonétique", "traduction française"]
    ]
  },
  ...
]
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error fetching from Gemini API: {e}, using fallback.")
        return FALLBACK_ARTICLES

async def generate():
    articles = fetch_articles()
    os.makedirs("audio", exist_ok=True)
    audio_data = {}
    
    for item in articles:
        aid = item["id"]
        filename = f"audio/a2_{aid}.mp3"
        spoken = f"{item['theme_ar']}. {item['text']}"
        tts = edge_tts.Communicate(spoken, VOICE, rate=RATE)
        await tts.save(filename)
        with open(filename, "rb") as f:
            audio_data[str(aid)] = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode('utf-8')}"
            
    full_speech = "مَوْجَزُ الْأَخْبَارِ لِلْمُسْتَوَى الْمُبْتَدِئِ. \n\n " + " \n\n ".join(
        [f"{it['theme_ar']}: {it['text']}" for it in articles]
    )
    tts_full = edge_tts.Communicate(full_speech, VOICE, rate=RATE)
    await tts_full.save("audio/a2_full.mp3")
    with open("audio/a2_full.mp3", "rb") as f:
        audio_data["full"] = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    cards_html = []
    for item in articles:
        aid = item["id"]
        vocab_rows = "".join([
            f'<div><strong class="font-arabic text-sm text-[var(--foreground)]">{ar}</strong> ({ph}) : {fr}</div>'
            for ar, ph, fr in item['vocab']
        ])
        cards_html.append(f"""
      <article id="card-{aid}" class="border border-[var(--border)] rounded-xl p-4 sm:p-5 transition-all bg-[var(--background)]">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div class="flex items-center gap-2">
            <span class="text-lg">{item['icon']}</span>
            <span class="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">{aid}. {item['theme']}</span>
            <span class="text-xs text-[var(--muted-foreground)] font-arabic font-semibold">({item['theme_ar']})</span>
          </div>
          <div class="flex items-center gap-2">
            <audio id="audio-{aid}" controls preload="metadata" class="w-full sm:w-56" onplay="handlePlay({aid})">
              <source src="{audio_data[str(aid)]}" type="audio/mp3">
            </audio>
          </div>
        </div>

        <p id="text-{aid}" dir="rtl" class="font-arabic text-xl leading-relaxed text-[var(--foreground)] my-3 tracking-wide select-text">
          {item['text']}
        </p>

        <div class="mt-3 pt-3 border-t border-[var(--border)]">
          <details class="text-xs group" open>
            <summary class="cursor-pointer text-blue-600 dark:text-blue-400 hover:underline font-semibold select-none">
              🇫🇷 Traduction & Vocabulaire clé (A2)
            </summary>
            <div class="mt-2 text-xs text-[var(--muted-foreground)] bg-[var(--card)] p-3 rounded-lg border border-[var(--border)] space-y-2">
              <p class="italic text-sm text-[var(--foreground)]">
                « {item['traduction']} »
              </p>
              <div class="pt-2 border-t border-[var(--border)] grid grid-cols-1 sm:grid-cols-2 gap-2">
                {vocab_rows}
              </div>
            </div>
          </details>
        </div>
      </article>
        """)

    html_body = f"""<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Revue de Presse Arabe - Quotidienne</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;600;700&display=swap');
    
    :root, html.light, [data-theme="light"] {{
      color-scheme: light;
      --background: #f8fafc;
      --card: #ffffff;
      --surface-variant: #f1f5f9;
      --foreground: #0f172a;
      --muted-foreground: #64748b;
      --border: #e2e8f0;
    }}

    html.dark, [data-theme="dark"] {{
      color-scheme: dark;
      --background: #0b1120;
      --card: #1e293b;
      --surface-variant: #151f32;
      --foreground: #f8fafc;
      --muted-foreground: #94a3b8;
      --border: #334155;
    }}

    .font-arabic {{
      font-family: 'Amiri', 'Cairo', 'Traditional Arabic', 'Simplified Arabic', Tahoma, serif;
    }}
    .font-ui {{
      font-family: 'Cairo', system-ui, -apple-system, sans-serif;
    }}
    .active-playing {{
      border-color: #3b82f6 !important;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4) !important;
      background: rgba(59, 130, 246, 0.04) !important;
    }}
    audio {{
      height: 36px;
    }}
    body {{
      background-color: var(--background);
      color: var(--foreground);
      transition: background-color 0.25s ease, color 0.25s ease;
    }}
  </style>
</head>
<body class="antialiased p-2 sm:p-5 font-ui">

  <div class="max-w-4xl mx-auto bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl shadow-xl overflow-hidden transition-all duration-200">
    
    <header class="p-5 sm:p-6 border-b border-[var(--border)] bg-[var(--surface-variant)] transition-colors duration-200">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300 mb-2">
            <span>🟢 Niveau Débutant (A2) • Vocabulaire Essentiel</span>
          </div>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-[var(--foreground)]">
            مَوْجَزُ الْأَخْبَارِ الْيَوْمِيّ • Revue Quotidienne
          </h1>
          <p class="text-xs sm:text-sm text-[var(--muted-foreground)] mt-1">
            Phrases courtes, syntaxe limpide, voyelles complètes (Tashkīl) et prononciation lente.
          </p>
        </div>

        <div class="flex items-center flex-wrap gap-2">
          <button id="themeToggleBtn" onclick="toggleTheme()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)] text-xs font-semibold hover:border-blue-400 transition-colors shadow-sm cursor-pointer" title="Basculer Mode Clair / Sombre">
            <span id="themeIcon">🌙</span>
            <span id="themeLabel">Mode Sombre</span>
          </button>

          <div class="flex items-center bg-[var(--background)] border border-[var(--border)] rounded-lg px-3 py-1.5 text-xs shadow-sm">
            <span class="text-[var(--muted-foreground)] mr-1.5 font-medium">Vitesse :</span>
            <select id="globalRate" onchange="updateAllRates(this.value)" class="bg-transparent text-[var(--foreground)] font-bold outline-none cursor-pointer">
              <option value="0.75">0.75x</option>
              <option value="0.85" selected>0.85x</option>
              <option value="1.0">1.0x</option>
            </select>
          </div>
        </div>
      </div>

      <div class="mt-4 p-3 bg-[var(--background)] border border-emerald-500/30 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="text-2xl">📻</span>
          <div>
            <div class="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Audio Intégral</div>
            <div class="text-sm font-semibold text-[var(--foreground)]">Écouter les 5 thèmes d'affilée</div>
          </div>
        </div>
        <audio id="audio-full" controls preload="metadata" class="w-full sm:w-64 max-w-full">
          <source src="{audio_data['full']}" type="audio/mp3">
        </audio>
      </div>
    </header>

    <main class="p-4 sm:p-6 space-y-6">
      {"".join(cards_html)}
    </main>

    <footer class="p-4 sm:p-5 border-t border-[var(--border)] bg-[var(--surface-variant)] text-xs text-[var(--muted-foreground)] flex flex-col sm:flex-row items-center justify-between gap-2 transition-colors duration-200">
      <span>💡 Mise à jour automatique chaque matin par GitHub Actions & Netlify.</span>
      <span class="font-medium">🌙 / ☀️ Thème Dark Mode</span>
    </footer>

  </div>

  <script>
    function applyTheme(theme) {{
      const root = document.documentElement;
      const icon = document.getElementById('themeIcon');
      const label = document.getElementById('themeLabel');
      
      if (theme === 'dark') {{
        root.classList.add('dark');
        root.classList.remove('light');
        root.setAttribute('data-theme', 'dark');
        if (icon) icon.innerText = '☀️';
        if (label) label.innerText = 'Mode Clair';
      }} else {{
        root.classList.add('light');
        root.classList.remove('dark');
        root.setAttribute('data-theme', 'light');
        if (icon) icon.innerText = '🌙';
        if (label) label.innerText = 'Mode Sombre';
      }}
      try {{
        localStorage.setItem('arabic_press_theme', theme);
      }} catch(e) {{}}
    }}

    function toggleTheme() {{
      const isDark = document.documentElement.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
      applyTheme(isDark ? 'light' : 'dark');
    }}

    (function initTheme() {{
      let preferred = 'light';
      try {{
        preferred = localStorage.getItem('arabic_press_theme');
      }} catch(e) {{}}
      if (!preferred) {{
        preferred = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
      }}
      applyTheme(preferred);
    }})();

    const allAudios = ['audio-full', 'audio-1', 'audio-2', 'audio-3', 'audio-4', 'audio-5'];

    function handlePlay(id) {{
      allAudios.forEach(audId => {{
        if (audId !== 'audio-' + id) {{
          const a = document.getElementById(audId);
          if (a && !a.paused) a.pause();
        }}
      }});
      for (let i = 1; i <= 5; i++) {{
        const card = document.getElementById('card-' + i);
        if (card) {{
          if (i === id) card.classList.add('active-playing');
          else card.classList.remove('active-playing');
        }}
      }}
    }}

    document.getElementById('audio-full').onplay = function() {{
      allAudios.forEach(audId => {{
        if (audId !== 'audio-full') {{
          const a = document.getElementById(audId);
          if (a && !a.paused) a.pause();
        }}
      }});
      for (let i = 1; i <= 5; i++) {{
        const card = document.getElementById('card-' + i);
        if (card) card.classList.remove('active-playing');
      }}
    }};

    function updateAllRates(rateVal) {{
      const rate = parseFloat(rateVal);
      allAudios.forEach(id => {{
        const a = document.getElementById(id);
        if (a) a.playbackRate = rate;
      }});
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      updateAllRates(document.getElementById('globalRate').value);
    }});
  </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_body)
    print("New index.html successfully generated!")

if __name__ == "__main__":
    asyncio.run(generate())
