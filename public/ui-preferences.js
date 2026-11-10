/** Simulator-only appearance and language preferences; never stores credentials. */
(() => {
  const messages = {
    pageTitle:['Murid Wukong — Simulator Merchant','Murid Wukong — Merchant Simulator'],
    skip:['Lewati ke konten','Skip to content'], theme:['Tampilan','Appearance'], language:['Bahasa','Language'], dark:['Gelap','Dark'], light:['Terang','Light'],
    tagline:['Satu akun. Banyak kemungkinan.','One account. More possibilities.'], headline:['Semua kebutuhan.','Your everyday needs.'], headlineAccent:['Satu langkah dekat.','One step closer.'],
    introduction:['Jelajahi layanan favoritmu bersama Murid Wukong. Mulai dari sini, lanjut ke VIA.','Explore your favorite services with Murid Wukong. Start here, continue with VIA.'],
    memberAccess:['Akses member.','Member access.'], memberCaption:['Satu akun untuk membuka layanan VIA.','One account to access VIA services.'], storyCaption:['Pengalaman merchant, dalam versi simulasi.','The merchant experience, in a simulation.'],
    welcome:['Selamat datang.','Welcome back.'], loginHint:['Masuk dengan akun demo untuk melanjutkan.','Sign in with a demo account to continue.'], username:['Username','Username'], password:['Password','Password'],
    usernamePlaceholder:['Masukkan username','Enter your username'], passwordPlaceholder:['Masukkan password','Enter your password'], showPassword:['Tampilkan password','Show password'], hidePassword:['Sembunyikan password','Hide password'], signIn:['Masuk sekarang','Sign in'], signingIn:['Sedang masuk…','Signing in…'],
    demoHint:['Gunakan akun demo dari pengelola.','Use a demo account from the operator.'], noRealMoney:['Simulasi ini tidak menggunakan uang sungguhan.','This simulation does not use real money.'], simulation:['Simulasi merchant · v1.0','Merchant simulation · v1.0'],
    greeting:['Senang kamu kembali,','Good to see you again,'], activeAccount:['Akun merchant aktif','Active merchant account'], accountName:['Akun Murid Wukong','Murid Wukong account'], active:['Aktif','Active'],
    topup:['Top up','Top up'], transfer:['Transfer','Transfer'], pay:['Bayar','Pay'], services:['Layanan','Services'], picks:['Pilihan buat kamu','Picked for you'], miniServices:['Mini App & layanan','Mini App & services'],
    phone:['Pulsa & data','Airtime & data'], electricity:['Listrik','Electricity'], bills:['Tagihan','Bills'], internet:['Internet','Internet'], transport:['Transport','Transport'], voucher:['Voucher','Vouchers'], more:['Lainnya','More'],
    unavailableTopup:['Top up belum tersedia','Top up is not available yet'], unavailableTransfer:['Transfer belum tersedia','Transfer is not available yet'], unavailablePay:['Bayar belum tersedia','Payments are not available yet'], unavailablePhone:['Pulsa dan data belum tersedia','Airtime and data are not available yet'], unavailableElectricity:['Listrik belum tersedia','Electricity is not available yet'], unavailableBills:['Tagihan belum tersedia','Bills are not available yet'], unavailableInternet:['Internet belum tersedia','Internet is not available yet'], unavailableTransport:['Transport belum tersedia','Transport is not available yet'], unavailableVoucher:['Voucher belum tersedia','Vouchers are not available yet'], unavailableMore:['Layanan lain belum tersedia','Other services are not available yet'],
    meetVia:['Kenalan dengan VIA','Meet VIA'], promoTitle:['Buka layanannya.','Open the service.'], promoAccent:['Langsung dari akunmu.','Right from your account.'], promoCopy:['Masuk sekali di merchant, lanjut ke Mini App tanpa login lagi.','Sign in once with your merchant and continue to the Mini App without signing in again.'],
    exploration:['Ruang eksplorasi','Explore the experience'], tryTitle:['Satu akun,','One account,'], tryAccent:['lanjut ke Mini App.','on to the Mini App.'], tryCopy:['Coba alur masuk merchant dan buka layanan VIA dari satu tempat.','Try merchant sign-in and access VIA services from one place.'], stepOne:['Masuk ke merchant','Sign in to the merchant'], stepTwo:['Buka Mini App','Open the Mini App'], stepThree:['Lanjut dengan akunmu','Continue with your account'], tryDemo:['Coba koneksi demo','Try demo connection'],
    finePrint:['VIA adalah pintu masuk Mini App. Layanan lainnya masih berupa ilustrasi dan belum dapat digunakan. Tidak ada saldo atau transaksi uang sungguhan pada simulator merchant ini.','VIA opens the Mini App. Other services are illustrations and are not available yet. This merchant simulator has no real-money balance or transactions.'], logout:['Keluar dari akun','Sign out'], navigation:['Navigasi utama','Main navigation'], home:['Beranda','Home'], account:['Akun','Account'], back:['Kembali','Back'],
    configReady:['VIA siap dibuka dari pilihan layanan.','VIA is ready to open from your services.'], configWaiting:['VIA belum terhubung. Coba koneksi demo sambil menunggu layanan tersedia.','VIA is not connected yet. Try the demo connection while the service is being prepared.'], configFailed:['Layanan belum bisa dimuat. Koneksi demo tetap dapat dicoba.','Services could not be loaded. You can still try the demo connection.'], logoutFailed:['Belum bisa keluar. Coba lagi.','Could not sign out. Please try again.'],
    invalidCredentials:['Username atau password belum cocok. Coba periksa kembali.','The username or password is incorrect. Please check and try again.'], originRejected:['Alamat aplikasi belum sesuai konfigurasi merchant. Hubungi pengelola.','The application address does not match the merchant configuration. Contact the operator.'], loginFailed:['Belum bisa masuk. Coba lagi atau hubungi pengelola demo.','Could not sign in. Try again or contact the demo operator.'],
    bridgeConnecting:['Menghubungkan akun ke Mini App…','Connecting your account to the Mini App…'], bridgeTimeout:['Mini App belum merespons. Coba kembali; jika berulang, hubungi pengelola.','The Mini App has not responded. Go back and try again; contact the operator if it continues.'], bridgeFailed:['Akun belum terhubung. Kembali ke merchant dan coba masuk lagi.','Your account is not connected. Return to the merchant and sign in again.'], bridgeConnected:['Terhubung dengan akun merchant kamu','Connected with your merchant account'],
    receiverTitle:['VIA — Koneksi demo','VIA — Demo connection'], receiverHeading:['Koneksi akunmu.','Your account connection.'], receiverCopy:['Halaman ini menguji apakah Mini App dapat menerima token dari akun merchant. Token tidak ditampilkan di halaman.','This page tests whether the Mini App can receive a token from the merchant account. The token is not displayed.'], receiverConnecting:['Menghubungkan ke akun merchant…','Connecting to the merchant account…'], receiverRetry:['Coba koneksi lagi','Try the connection again'], receiverNote:['Ini receiver demo, bukan halaman pembelian PPOB. Tidak ada transaksi atau pembayaran yang dilakukan.','This is a demo receiver, not a PPOB purchase page. No transactions or payments are made.'], receiverError:['Koneksi gagal. Kembali ke merchant dan coba lagi.','Connection failed. Return to the merchant and try again.']
  };
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const state = {
    theme: read('mw.theme') || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'),
    language: read('mw.language') || 'id'
  };
  if (!['dark','light'].includes(state.theme)) state.theme='dark';
  if (!['id','en'].includes(state.language)) state.language='id';
  const t = key => messages[key]?.[state.language==='en'?1:0] ?? key;
  function apply() {
    document.documentElement.dataset.theme=state.theme;
    document.documentElement.lang=state.language;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content',state.theme==='light'?'#f5f8f6':'#101313');
    document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n);});
    for (const attribute of ['placeholder','aria-label']) {
      document.querySelectorAll(`[data-i18n-${attribute}]`).forEach(el=>el.setAttribute(attribute,t(el.getAttribute(`data-i18n-${attribute}`))));
    }
    document.querySelectorAll('[data-preference]').forEach(el=>{el.value=state[el.dataset.preference];});
    if (document.body?.dataset.page==='receiver') document.title=t('receiverTitle');
    else document.title=t('pageTitle');
    window.dispatchEvent(new Event('mw:preferences'));
  }
  function set(name,value) {
    if (!['theme','language'].includes(name)) return;
    if (!(name==='theme'?['light','dark']:['id','en']).includes(value)) return;
    state[name]=value;
    try { localStorage.setItem(name==='theme'?'mw.theme':'mw.language',value); } catch { /* Session-only preferences still work when storage is blocked. */ }
    apply();
  }
  window.MerchantUI={t,apply,set,state};
  document.documentElement.dataset.theme=state.theme;
  document.documentElement.lang=state.language;
  document.addEventListener('DOMContentLoaded',()=>{
    document.querySelectorAll('[data-preference]').forEach(el=>el.addEventListener('change',()=>set(el.dataset.preference,el.value)));
    apply();
  });
  window.addEventListener('storage',event=>{
    if (event.key===null || ['mw.theme','mw.language'].includes(event.key)) {
      const theme=read('mw.theme'), language=read('mw.language');
      if (['dark','light'].includes(theme)) state.theme=theme;
      if (['id','en'].includes(language)) state.language=language;
      apply();
    }
  });
})();
