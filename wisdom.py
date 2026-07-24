"""
wisdom.py
----------
Mashhoor traders aur trading books ke PROVEN usool — plain Roman Urdu mein.
Yeh khud research se liye gaye asal principles hain (koi copyrighted text nahi,
sirf usool + attribution). Streamlit tab mein render() se dikhte hain.
"""

import streamlit as st


# (Usool, tafseel, source) — money management
MONEY_RULES = [
    ("1% / 2% Risk Rule",
     "Ek trade par apni total capital ka sirf 1-2% risk karo. Yun 10 trade "
     "lagataar haar bhi jao to bhi account zinda rehta hai.",
     "Turtle Traders / Van Tharp"),
    ("Cut losses, let winners run",
     "Nuqsan wale trade se JALDI niklo (stop-loss), aur nafa wale ko chalne do. "
     "Yeh ek jumla hi zyadatar traders ki kamyabi ka raaz hai.",
     "Richard Dennis (Turtles)"),
    ("Risk-Reward kam se kam 1:2",
     "Jitna risk (stop tak) le rahe ho, target us se kam se kam DOGUNA rakho. "
     "Aise aadhe trade galat hon tab bhi aap profit mein rehte ho.",
     "Classic money management"),
    ("Pyramiding (soch samajh kar)",
     "Jab trade aapke haq mein chale to hi position barhao — galat ja rahe trade "
     "mein aur paisa 'average down' karke mat daalo.",
     "Turtle Traders"),
    ("Kabhi bhi poori capital ek jagah nahi",
     "Diversify karo — sab kuch ek coin/stock par mat lagao. Ek doobe to sab na doobe.",
     "Common wisdom"),
]

# Trading psychology — Mark Douglas (Trading in the Zone) ke asal ideas
PSYCH_RULES = [
    ("Probability mein socho, yaqeen mein nahi",
     "Koi bhi single trade jeet ya haar sakta hai — yeh normal hai. Aap sirf "
     "apne 'edge' ko baar baar dohrao; nafa 100 trades ke set par banta hai, ek par nahi.",
     "Mark Douglas"),
    ("Process > Outcome",
     "Har trade ka nateeja mat dekho — apne plan par amal dekho. Achha trade wo "
     "hai jo plan ke mutabiq liya gaya, chahe nuqsan hua ho.",
     "Mark Douglas"),
    ("Fear aur Greed sab se bade dushman",
     "Dar se achha trade miss ho jaata hai, laalach se bura trade le liya jaata hai. "
     "Rules pehle se likho aur unhi par chalo — jazbaat mein faisla mat karo.",
     "Mark Douglas"),
    ("Discipline = Consistency",
     "Ek behtreen strategy bhi bina discipline ke haar jaati hai. Rozana wahi rules, "
     "wahi risk, wahi sabr — yeh boring lagta hai lekin yehi jeetata hai.",
     "Trading in the Zone"),
    ("Revenge trading se bacho",
     "Nuqsan ke foran baad 'wapas jeetne' ke liye jaldbazi mein trade mat karo — "
     "yeh aksar aur bada nuqsan deta hai. Break lo, phir socho.",
     "Pro traders"),
]

# Pre-trade checklist (har trade se pehle)
CHECKLIST = [
    "Trend meri direction mein hai? (Multi-Timeframe tab check kiya?)",
    "Entry ki wajah clear hai? (kam se kam 2-3 signals agree karte hain?)",
    "Stop-loss kahan lagega — pehle se decide kiya?",
    "Target kahan hai — Risk:Reward 1:2 ya behtar?",
    "Is trade par sirf 1-2% risk le raha hoon? (Risk Calculator use kiya?)",
    "Main jazbaat (dar/laalach/badla) mein to nahi? Dimaag thanda hai?",
]


def render() -> None:
    st.subheader("🎓 Pro Traders ke Proven Usool")
    st.caption("Yeh duniya ke mashhoor traders aur trading books ke asal usool hain — "
               "inhe seekhein aur amal karein. Strategy se ZYADA yeh usool paisa bachate hain.")

    st.markdown("### 💰 Money Management (paisa bachane ke usool)")
    for title, detail, src in MONEY_RULES:
        with st.container(border=True):
            st.markdown(f"**{title}**  \n{detail}")
            st.caption(f"— {src}")

    st.markdown("### 🧠 Trading Psychology (dimaag ka control)")
    st.caption("Mashhoor kitab *'Trading in the Zone'* (Mark Douglas) ke asal ideas:")
    for title, detail, src in PSYCH_RULES:
        with st.container(border=True):
            st.markdown(f"**{title}**  \n{detail}")
            st.caption(f"— {src}")

    st.markdown("### ✅ Har Trade se Pehle — Checklist")
    st.write("Yeh 6 sawal har trade se PEHLE khud se poochein. Ek ka bhi jawab 'nahi' ho to trade mat karein:")
    for i, item in enumerate(CHECKLIST, 1):
        st.checkbox(f"{i}. {item}", key=f"chk_{i}")

    st.info("💡 **Sab se bada sabaq:** Kamyaab trader wo nahi jo hamesha sahi hota hai — "
            "wo hai jo apne nuqsan chhote rakhta hai aur discipline se apne usool par chalta hai.")

    st.caption("Sources: Turtle Traders (Richard Dennis), 'Trading in the Zone' (Mark Douglas), "
               "classic money-management principles. Sirf education ke liye.")
