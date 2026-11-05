# GitHub Profile “Nocturne Dossier” Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merombak profil GitHub Nothrovo menjadi dossier profesional Cyber SOC dan web systems yang lebih padat, terbaca pada mobile, dan tetap memiliki identitas Reze/Chainsaw Man tanpa membiarkan dekorasi mengalahkan karya nyata.

**Architecture:** README tetap berupa satu kolom responsif berbasis Markdown dan subset HTML yang didukung GitHub. Informasi kritis dirender sebagai teks native; gambar eksternal hanya dipakai untuk atmosfer dan telemetry tambahan. Hero dan epilog boleh terpusat, sedangkan ringkasan, proyek, kompetensi, dan stack menggunakan alur rata kiri agar cepat dipindai.

**Tech Stack:** GitHub Flavored Markdown, HTML aman GitHub, Shields.io, GitHub Readme Stats, satu GIF eksternal terverifikasi, GitHub CLI (`gh`), pemeriksaan URL paralel, browser nyata untuk screenshot desktop/mobile.

**Spec:** `HANDOVER.md`, screenshot audit pengguna `dashboard_20261105_155908_1bc8efe6_image_777515.png`, dan keputusan desain dalam dokumen ini.

## Global Constraints

- Ini adalah **profil profesional bertema Reze**, bukan halaman fandom.
- Pertahankan palet identitas `#0e0a14`, `#120d1c`, `#38244d`, `#ff4b72`, `#b388ff`, `#e0d6eb`, dan `#9b8ea9` hanya pada aset yang memang mendukung warna khusus.
- Nama, peran, ringkasan, judul section, proyek, dan kontak wajib berupa teks native GitHub—bukan typing SVG.
- Gunakan maksimal satu GIF dan maksimal dua kartu statistik.
- Jangan memakai CSS, JavaScript, flex/grid, media query, positioning absolut, atau layout lain yang akan disaring GitHub.
- Jangan memakai tabel untuk proyek, paragraf, atau layout dua kolom; tabel GitHub menyempit alih-alih menumpuk dengan baik pada mobile.
- Gunakan alignment terpusat hanya untuk hero, telemetry, dan epilog; isi profesional utama rata kiri.
- Jangan mengarang angka, hasil, status produksi, afiliasi, atau klaim keamanan. Hanya gunakan fakta yang tersedia di repositori publik atau telah dikonfirmasi pengguna.
- Jangan mengubah atau mendorong `README.md` sebelum plan disetujui pengguna.
- Implementasi akhir harus dapat dipahami walaupun seluruh gambar eksternal gagal dimuat.
- Sebelum perubahan README, buat backup Git lokal yang mudah dikembalikan (branch atau tag), bukan file `.bak` yang ikut tampil di profil.

## Arah Desain yang Dipilih

**Nama:** Nocturne Dossier

**Ide:** “Controlled detonation”—Reze memberi pembuka atau penutup sinematik, tetapi bagian tengah menjadi dossier operasi yang tenang, padat, dan berbasis bukti.

**Mengapa dipilih:** Arah ini langsung memperbaiki empat masalah pada hasil nyata: teks mini di dalam SVG, pusat alignment berlebihan, whitespace buatan dari `<br>`, dan statistik yang lebih dominan daripada karya. Alternatif dua kolom ditolak karena rapuh pada mobile; alternatif semua-terpusat ditolak karena masih mewarisi pola poster yang sulit dipindai.

## Struktur Akhir yang Disetujui untuk Implementasi

1. **Hero identitas** — nama, handle, peran, ringkasan profesional, dan tautan utama sebagai teks native.
2. **Current Focus** — tiga fokus konkret: SOC/incident response, security automation, dan backend/web systems.
3. **Selected Work — Field Reports** — Arbiter, Neuropetra-IP, dan MedChain sebagai bukti kerja.
4. **Security Operations — Defense Matrix** — kompetensi yang dikelompokkan berdasarkan fungsi.
5. **Engineering Stack — Systems** — stack inti yang didukung oleh proyek nyata.
6. **GitHub Activity — Telemetry** — maksimal dua kartu pendukung, bukan pusat narasi.
7. **Contact — Transmission** — email, LinkedIn, GitHub, dan SOC LAB dengan label langsung.
8. **Reze epilog** — maksimal satu visual dan satu kutipan pendek sebagai tanda tangan visual.

## Review Focus

- **Kegagalan aset eksternal:** nama, peran, proyek, dan kontak tetap lengkap ketika GIF, badge, atau kartu statistik tidak termuat.
- **Viewport sempit 320 px:** tidak ada overflow horizontal, teks yang terpotong, atau kartu mini yang mustahil dibaca.
- **Tema terang GitHub:** semua aset berkustom warna tetap memiliki latar sendiri dan teks tidak menghilang.
- **Data proyek tidak terverifikasi:** deskripsi harus bersumber dari metadata/README repo; jangan menambahkan hasil terukur tanpa bukti.
- **Sanitasi GitHub:** jangan bergantung pada `target="_blank"`, inline style, `max-width` CSS, atau elemen yang mungkin dihapus GitHub.

---

### Task 1: Baseline, Backup, dan Validator Struktur

**Files:**
- Create: `scripts/validate_profile_readme.py`
- Create: `docs/profile-redesign/baseline.md`
- Preserve: `README.md`

**Interfaces:**
- Consumes: README lama dan endpoint publik semua aset eksternal.
- Produces: validator deterministik yang menerima path README dan keluar `0` bila seluruh constraint struktural lulus.

- [ ] **Step 1: Catat baseline sebelum perubahan**

Simpan hash commit awal, ukuran README, jumlah `<br>`, typing SVG, GIF, badge, kartu statistik, dan URL eksternal di `docs/profile-redesign/baseline.md`. Sertakan masalah visual yang tampak pada screenshot: teks terlalu kecil, whitespace panjang, semua konten terpusat, dan statistik lebih dominan daripada karya.

- [ ] **Step 2: Buat titik pemulihan Git**

Buat branch backup bernama `backup/profile-before-nocturne-dossier` pada commit awal. Verifikasi branch menunjuk ke commit yang sama dengan `main` sebelum edit.

- [ ] **Step 3: Tulis validator yang gagal terhadap README lama**

`validate_profile_readme.py` harus memeriksa setidaknya:

- tepat satu `<h1>` atau heading level-1 native;
- teks native memuat `Hadi Nurhasan Darma`, `Cyber SOC Analyst`, dan `Web Developer`;
- link ke `Arbiter`, `Neuropetra-IP`, dan `MedChain` ada sebelum URL statistik pertama;
- jumlah `readme-typing-svg` = `0`;
- jumlah GIF ≤ `1`;
- jumlah kartu statistik ≤ `2`;
- jumlah `<br>` manual ≤ `2`;
- URL streak card tidak ada;
- semua `<img>` memiliki `alt` non-kosong;
- tidak ada `<style>`, `<script>`, `style=`, atau tabel layout;
- alamat email, GitHub, dan LinkedIn tersedia sebagai link nyata.

- [ ] **Step 4: Jalankan validator untuk membuktikan baseline gagal**

Run: `python scripts/validate_profile_readme.py README.md`

Expected: non-zero dengan kegagalan pada heading native, tiga proyek, typing SVG, jumlah GIF, jumlah `<br>`, dan streak card.

- [ ] **Step 5: Commit validator dan baseline**

```bash
git add scripts/validate_profile_readme.py docs/profile-redesign/baseline.md
git commit -m "test: define profile redesign constraints"
```

### Task 2: Bangun Hero Native dan Alur Informasi Profesional

**Files:**
- Modify: `README.md:1-20`
- Test: `scripts/validate_profile_readme.py`

**Interfaces:**
- Consumes: identitas publik Nothrovo, email dan LinkedIn yang sudah ada, serta Global Constraints.
- Produces: hero native yang tetap bermakna tanpa gambar dan menjadi fondasi section berikutnya.

- [ ] **Step 1: Ganti hero berbasis gambar dengan identitas native**

Gunakan satu `# Hadi Nurhasan Darma — Nothrovo`, lalu satu baris peran `Cyber SOC Analyst | Web Developer`. Tambahkan ringkasan 2–3 kalimat yang menjelaskan fokus pada investigasi SOC, incident response, security automation, dan backend/web systems tanpa buzzword atau klaim senioritas baru.

- [ ] **Step 2: Tempatkan tautan utama pada hero**

Tampilkan Email, LinkedIn, GitHub, dan `SOC LAB` secara ringkas. `SOC LAB` adalah afiliasi teks, bukan tombol palsu kecuali tersedia URL resmi yang telah diverifikasi.

- [ ] **Step 3: Tambahkan Current Focus sebagai teks**

Gunakan tiga bullet pendek dan konkret: SOC/incident response; automasi dan threat-intelligence correlation; backend/web systems. Jangan memakai badge pada section ini.

- [ ] **Step 4: Hilangkan divider eksternal dan spacer buatan**

Ganti capsule-render dengan separator Markdown bila benar-benar diperlukan. Jangan menambah rangkaian `<br>` untuk mengatur ritme.

- [ ] **Step 5: Verifikasi hero tanpa gambar**

Buka README dengan network image blocking atau inspeksi source rendered HTML. Expected: identitas, peran, ringkasan, fokus, dan kontak pertama tetap langsung terbaca.

- [ ] **Step 6: Commit hero**

```bash
git add README.md
git commit -m "feat: make profile identity native and readable"
```

### Task 3: Tambahkan Selected Work Berbasis Bukti Nyata

**Files:**
- Modify: `README.md` setelah Current Focus
- Test: `scripts/validate_profile_readme.py`

**Interfaces:**
- Consumes: metadata dan README publik `Nothrovo/Arbiter`, `Nothrovo/Neuropetra-IP`, dan `Nothrovo/MedChain`.
- Produces: tiga field report vertikal yang memperlihatkan kemampuan sebelum badge dan statistik.

- [ ] **Step 1: Tambahkan heading `## Selected Work — Field Reports`**

Judul profesional berada di depan; tema berada setelah em dash agar pemindai cepat tetap memahami section.

- [ ] **Step 2: Tulis entry Arbiter**

Sumber fakta: deskripsi repo publik dan README. Soroti bahwa Arbiter adalah investigation desk air-gapped untuk normalisasi telemetry Wazuh, korelasi threat intelligence, incident case authoring, dan forensic reporting. Tautkan judul ke `https://github.com/Nothrovo/Arbiter`. Jangan menyebut angka tes atau status enterprise kecuali diverifikasi lagi saat implementasi.

- [ ] **Step 3: Tulis entry Neuropetra-IP**

Sumber fakta: deskripsi repo publik dan README. Soroti investigasi indikator IPv4/IPv6, evidence/provider roster lokal, perbandingan reputasi dengan sinyal lokal, dan bounded feed export. Tautkan ke `https://github.com/Nothrovo/Neuropetra-IP`.

- [ ] **Step 4: Tulis entry MedChain**

Sumber fakta: deskripsi repo publik dan README. Nyatakan sebagai purwarupa rekam medis terdistribusi lokal yang memakai SHA-256 untuk deteksi manipulasi dan RSA untuk validasi tanda tangan digital dokter. Tautkan ke `https://github.com/Nothrovo/MedChain`; jangan mengesankan penggunaan produksi.

- [ ] **Step 5: Gunakan pola entry yang konsisten**

Setiap proyek berisi: nama bertaut, satu kalimat masalah/tujuan, satu kalimat kontribusi atau kemampuan inti, dan stack singkat hanya bila terverifikasi dari repo. Jangan memakai tabel, gambar kartu eksternal, atau paragraf panjang.

- [ ] **Step 6: Verifikasi urutan narasi**

Run: `python scripts/validate_profile_readme.py README.md`

Expected sementara: pemeriksaan urutan tiga proyek terhadap statistik lulus; constraint lain boleh tetap gagal sampai task pemiliknya selesai.

- [ ] **Step 7: Commit selected work**

```bash
git add README.md
git commit -m "feat: feature verified security and systems work"
```

### Task 4: Rapikan Kompetensi dan Stack Tanpa Badge Wall

**Files:**
- Modify: bagian lama `Defense Matrix` dan `Munitions & Systems` dalam `README.md`
- Test: `scripts/validate_profile_readme.py`

**Interfaces:**
- Consumes: stack lama yang sudah tercantum dan bukti penggunaan dari selected work.
- Produces: dua section rata kiri, berkelompok, dan mudah dipindai.

- [ ] **Step 1: Buat `## Security Operations — Defense Matrix`**

Kelompokkan kompetensi sebagai teks/badge ringkas:

- Detection & SIEM: Wazuh, Elasticsearch;
- Incident Response & DFIR: Incident Response, DFIR IRIS;
- Automation & Intelligence: n8n/SOAR, threat-intelligence correlation;
- Network & Application Security: Wireshark, Burp Suite, Linux hardening.

Jangan memberi semua item bobot visual yang sama bila hanya sebagian didukung proyek unggulan.

- [ ] **Step 2: Buat `## Engineering Stack — Systems`**

Kelompokkan:

- Languages: Python, TypeScript/JavaScript;
- Backend & Data: FastAPI, Node.js, PostgreSQL, Redis;
- Platform: Docker, Arch Linux, Git.

- [ ] **Step 3: Batasi badge dan hapus ukuran paksa**

Jika badge dipertahankan, gunakan maksimal 12 badge total untuk dua section, tanpa `height="40"`, tanpa forced row breaks, dan semua badge interaktif harus menuju dokumentasi resmi. Informasi yang tidak muat sebagai badge tetap berupa teks native.

- [ ] **Step 4: Verifikasi wrapping dan density**

Pada viewport 320/375/430 px, pastikan badge membungkus alami tanpa overflow. Pada desktop, pastikan section tidak berubah menjadi satu baris tombol panjang yang sulit dipindai.

- [ ] **Step 5: Commit kompetensi**

```bash
git add README.md
git commit -m "refactor: group security and engineering capabilities"
```

### Task 5: Sederhanakan Telemetry, Kontak, dan Epilog

**Files:**
- Modify: bagian lama `Combat Telemetry`, climax, dan `Transmission Matrix` dalam `README.md`
- Test: `scripts/validate_profile_readme.py`

**Interfaces:**
- Consumes: endpoint statistik andal dan dua GIF lama.
- Produces: maksimal dua kartu statistik, satu jalur kontak jelas, dan satu visual Reze sebagai signature.

- [ ] **Step 1: Buat `## GitHub Activity — Telemetry`**

Pertahankan GitHub Stats. Pertahankan Top Languages hanya bila hasil saat implementasi masih representatif; beri konteks singkat bahwa bahasa dihitung dari repositori publik. Hapus streak card dan segala penyebutan grade sebagai ukuran kemampuan.

- [ ] **Step 2: Buat kontak native**

Gunakan `## Contact — Transmission` dengan email, LinkedIn, dan GitHub sebagai link teks atau badge standar yang terbaca. Jangan menaruh email lengkap di dalam gambar badge. Tempatkan section ini sebelum epilog agar tindakan profesional tidak terkubur.

- [ ] **Step 3: Pilih tepat satu GIF berdasarkan audit aset**

Verifikasi kedua kandidat: status HTTP, tipe MIME, dimensi, frame count, ukuran file, dan waktu fetch. Pilih satu yang paling kuat secara visual dan tetap di bawah 2.5 MB. Preferensi desain: gunakan visual Reze tenang sebagai signature bila ia lebih koheren dengan profil profesional; gunakan ledakan hanya bila crop dan geraknya tidak mendominasi kontak.

- [ ] **Step 4: Ubah epilog menjadi satu momen ringkas**

Tampilkan satu GIF dengan lebar deklaratif tidak lebih dari 420 px dan alt deskriptif, lalu satu blockquote statis pendek. Hapus typing SVG `PULL THE PIN... BOOM!` dan quote looping. Bila punchline dipertahankan, jadikan teks native, bukan gambar.

- [ ] **Step 5: Jalankan validator lengkap**

Run: `python scripts/validate_profile_readme.py README.md`

Expected: exit `0`; typing SVG = 0, GIF ≤ 1, stats ≤ 2, `<br>` ≤ 2, streak = 0, semua informasi kritis native.

- [ ] **Step 6: Commit penutup**

```bash
git add README.md
git commit -m "refactor: simplify telemetry and Reze signature"
```

### Task 6: Verifikasi Visual, Link, Sanitasi, dan Live GitHub

**Files:**
- Create: `docs/profile-redesign/final-audit.md`
- Modify: `README.md` hanya bila audit menemukan masalah
- Test: `scripts/validate_profile_readme.py`

**Interfaces:**
- Consumes: README final lokal dan renderer live GitHub.
- Produces: bukti tekstual dan screenshot bahwa desain lulus desktop, mobile, light/dark, serta tidak memiliki link rusak.

- [ ] **Step 1: Validasi syntax dan struktur**

Jalankan validator final dan markdown lint bila tersedia. Pastikan tidak ada tag HTML tak tertutup, `style=`, script, tabel layout, atau whitespace manual berlebihan.

- [ ] **Step 2: Periksa semua URL secara paralel**

Ekstrak seluruh `href` dan `src`, deduplikasi, lalu cek dengan concurrency dan retry terbatas. Expected: semua link langsung dan aset penting menjawab sukses; redirect resmi diperbolehkan dan dicatat. Endpoint yang tetap gagal harus diganti atau dihapus, bukan diabaikan.

- [ ] **Step 3: Render dan screenshot lokal**

Render GFM dengan tool lokal yang paling mendekati GitHub, lalu ambil screenshot pada 320, 375, 430, 768, dan lebar desktop. Verifikasi tidak ada overflow horizontal, teks mini, kartu terpotong, atau blank band besar.

- [ ] **Step 4: Uji kegagalan gambar**

Blokir request image eksternal atau ganti sementara dengan respons gagal di renderer lokal. Expected: identitas, ringkasan, proyek, kompetensi, dan kontak tetap dapat dipahami lengkap.

- [ ] **Step 5: Independent design review**

Reviewer segar menilai screenshot dengan fokus: hierarki, density, alignment, keterbacaan, dominasi anime, dan mobile. Perbaiki temuan blocking; jangan menambah ornamen untuk mengisi ruang.

- [ ] **Step 6: Catat perbandingan before/after**

`final-audit.md` memuat nilai sebelum/sesudah untuk jumlah typing SVG, GIF, badge, stats card, `<br>`, proyek unggulan, dan link gagal; sertakan path screenshot audit.

- [ ] **Step 7: Commit hasil audit**

```bash
git add README.md docs/profile-redesign/final-audit.md scripts/validate_profile_readme.py
git commit -m "test: verify profile readability and resilience"
```

- [ ] **Step 8: Push hanya setelah persetujuan pengguna**

Push `main`, lalu buka `https://github.com/Nothrovo` di browser nyata. Ambil screenshot live pada desktop dan mobile; baca ulang target persis untuk memastikan GitHub tidak menyaring elemen penting.

- [ ] **Step 9: Verifikasi endpoint live**

Expected:

- nama/peran/ringkasan terlihat sebelum visual anime;
- tiga selected works muncul sebelum telemetry;
- tidak ada teks penting di dalam typing SVG;
- maksimal satu GIF dan dua kartu statistik;
- kontak ditemukan sebelum epilog;
- tidak ada overflow atau whitespace kosong lebih tinggi dari kira-kira setengah viewport;
- tema Reze masih terbaca melalui satu visual, palet aset, penamaan sekunder, dan satu kutipan—tanpa mengalahkan karya.

## Acceptance Criteria Final

- [ ] Hero native berisi nama, handle, peran, ringkasan, dan minimal dua jalur kontak.
- [ ] Arbiter, Neuropetra-IP, dan MedChain hadir sebelum statistik, masing-masing dengan deskripsi faktual dan link.
- [ ] Tidak ada `readme-typing-svg` untuk informasi apa pun.
- [ ] Maksimal satu GIF, dua kartu statistik, dua `<br>` manual, dan 12 badge teknologi/security.
- [ ] Streak card dan capsule divider eksternal telah dihapus.
- [ ] Tidak ada tabel layout, inline CSS, JavaScript, atau elemen yang bergantung pada sanitasi longgar.
- [ ] Semua gambar memiliki alt text bermakna; semua badge yang tampak interaktif memiliki tujuan valid.
- [ ] Tidak ada overflow pada 320/375/430 px dan tidak ada informasi inti yang membutuhkan zoom.
- [ ] Profil tetap berguna ketika gambar eksternal diblokir.
- [ ] Semua URL final terverifikasi dan render live GitHub telah dibaca kembali setelah push.
- [ ] Screenshot before/after memperlihatkan karya profesional sebagai fokus utama dan Reze sebagai framing visual.

## Self-Review Plan

- **Spec coverage:** Semua keluhan pengguna—space kosong, teks kecil, komposisi kurang rapi/cantik—dipetakan ke penghapusan spacer, teks native, restrukturisasi narasi, dan verifikasi screenshot multi-viewport.
- **Constraint coverage:** Plan hanya memakai kemampuan yang realistis untuk GitHub README; tidak mengandalkan CSS/JS atau responsive grid palsu.
- **Content grounding:** Tiga proyek berasal dari repo publik nyata; plan melarang metrik dan hasil rekaan.
- **Negative testing:** Kegagalan aset eksternal, mobile 320 px, light theme, sanitasi GitHub, dan URL gagal memiliki langkah tes eksplisit.
- **Deployment safety:** Backup branch dibuat sebelum edit, implementasi dicicil per commit, dan push/live verification hanya setelah persetujuan pengguna.
