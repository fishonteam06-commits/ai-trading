# 🔒 Security — App ki hifazat ki layers

Yeh app online (public internet) par jaane ke liye tayyar hai, is liye ismein
kai security layers daali gayi hain. Neeche har ek ka khulasa hai.

---

## 1. 🔑 Login Password Gate (`auth.py`)
- App khulte hi **password** maangti hai. Sahi password ke baghair kuch nazar nahi aata.
- Password **code mein nahi** — Streamlit ke **secure secrets vault** mein rehta hai.
- **Constant-time comparison** (`hmac.compare_digest`) — timing attacks se bacha hua.
- **Hashed password** support (SHA-256) — plain password rakhne ki zaroorat nahi.
- **Brute-force slowdown** — bar bar ghalat password par delay lag jaata hai.
- **Session timeout** — 8 ghante baad dobara login. **Logout button** bhi hai.

**Set kaise karein:** `.streamlit/secrets.toml` (local) ya Cloud → Settings → Secrets:
```
app_password = "ApnaMazbootPassword"
```

## 2. 🗝️ Secrets Management
- Koi password/API key kabhi **code ya GitHub par nahi** jaati.
- `.gitignore` `secrets.toml` ko block karta hai (galti se upload nahi hoga).
- Cloud par secrets encrypted vault mein rehte hain.

## 3. 🛡️ Input Validation (`data_sources.py`)
- Har symbol **sanitize** hota hai — sirf `A-Z 0-9 . - =` allowed, max 15 characters.
- Ajeeb/khatarnaak input (injection attempts, lambe strings) **block** ho jaata hai.
- `limit` bhi safe range (10–1000) mein clamp hota hai.

## 4. 🔐 HTTPS (Streamlit Cloud automatic)
- Deploy hone par link `https://` hota hai — data encrypted travel karta hai.
- Aapko kuch nahi karna, yeh khud-ba-khud on hota hai.

## 5. 🚫 API keys — per user, session-only
- Har user apni AI key **apne browser** mein daalta hai — kisi aur ko nazar nahi aati.
- Key kahin **save/log nahi** hoti, sirf us session ke liye memory mein.
- (Optional) Agar aap chahein sab ke liye ek hi key ho, to secrets mein daal sakte hain.

## 6. ⚙️ Safe defaults
- AI call sirf **button dabane par** (auto nahi) — taake koi aapki key/limit spam na kare.
- Tool **trades execute nahi karta** — sirf analysis. Yani hack ho bhi jaye to
  koi aapka paisa nahi nikaal sakta (koi broker/wallet connected hi nahi).

---

## ✅ Deploy se pehle checklist

- [ ] `secrets.toml` GitHub par upload **NAHI** kiya (sirf `config.toml`)
- [ ] Cloud → Settings → Secrets mein `app_password` set kiya
- [ ] Password mazboot hai (8+ characters, guess-proof)
- [ ] App khol kar test kiya — login maang rahi hai
- [ ] (Optional) Hashed password use kiya (`app_password_hash`)

---

## ⚠️ Yeh app kya NAHI karti (aapki hifazat ke liye)
- Aapke bank/exchange/wallet se **connect nahi** hoti.
- Aapka paisa khud **buy/sell nahi** karti.
- Aapki koi financial info nahi maangti.

Is liye chahe app public ho, aapka **paisa hamesha aapke apne control** mein rehta hai.
Yeh sirf analysis dikhati hai — amal aap khud apne broker par karte hain.
