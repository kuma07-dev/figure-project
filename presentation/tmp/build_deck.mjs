import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const root = "C:/Users/student/Desktop/ichiban-arbitrage-system";
const shot = "C:/Users/student/Desktop/網頁截圖";
const starter = `${root}/presentation/tmp/template-starter.pptx`;
const output = `${root}/presentation/ichiban-arbitrage-midterm.pptx`;

const deck = await PresentationFile.importPptx(await FileBlob.load(starter));

const text = {
  "sh/5sfepcfe":"ICHIBAN PRICE MONITORING MVP",
  "sh/547294r6":"台日一番賞\n價格監測系統",
  "sh/k3yl0zql":"把日本樂天刊登價格保存成歷史快照，加入價格觀察訊號與跨境成本試算。",
  "sh/65g3298r":"Python",
  "sh/sryl4zqx":"MySQL",
  "sh/utg3698n":"Flask",
  "sh/hofulsf2":"Chart.js",
  "sh/vmdcj2xw":"MVP 範圍：Rakuten 監測、歷史價格、簡易預警與成本試算；不宣稱穩定套利。",
  "sh/4r6dg7et":"01",
  "sh/cnupgny5":"ICHIBAN PRICE MONITORING MVP",
  "sh/9072xkry":"日本商品很多，但只看當下刊登價，還無法回答「值不值得繼續觀察」",
  "sh/ozy1ofad":"02",
  "sh/b29kza94":"我們先做一條小而完整的資料鏈：從指定角色搜尋商品、保存快照、看中位數，再把跨境成本一起算進來。",
  "sh/x4r21kru":"01",
  "sh/w3i1sfa9":"價格分散",
  "sh/r65knqtk":"同一角色有多筆刊登，單筆價格容易被高價或低價商品影響。",
  "sh/ove9o7yd":"02",
  "sh/9wnqhczy":"趨勢不清楚",
  "sh/mtwrmxg7":"只看今天的價格，無法分辨是短期波動還是正在變動。",
  "sh/wjy9sry9":"03",
  "sh/xk7qlczu":"成本常被漏算",
  "sh/ahwrqhgj":"匯率、代購費、物流和平台費會改變真正的保本價格。",
  "sh/bip8jmho":"所以這個 MVP 是市場觀察與可行性試算，不是保證獲利的套利系統。",
  "sh/re9g7yxo":"ICHIBAN PRICE MONITORING MVP",
  "sh/cza94vmx":"系統把 Rakuten 搜尋結果整理成可回看的價格資料",
  "sh/d0jax03i":"03",
  "sh/3ah8rqlg":"1",
  "sh/obq90bml":"Rakuten API",
  "sh/pcjqtg36":"依啟用追蹤角色的日文關鍵字查詢商品資料。",
  "sh/n6ls3alk":"2",
  "sh/n2l4fq98":"資料清洗",
  "sh/m1c3mlsn":"排除套組、預購、福袋與 ¥500–¥30,000 範圍外商品。",
  "sh/83ulovat":"3",
  "sh/v6l4jq94":"MySQL",
  "sh/a5c3ql8z":"商品 URL 去重；同一商品同一天最多保存一筆價格快照。",
  "sh/w7ulsvqp":"4",
  "sh/ja54na9g":"Flask",
  "sh/i9w3u58v":"查詢最新快照與角色歷史資料，提供網站頁面。",
  "sh/f29gbyx0":"5",
  "sh/03ix43e5":"Frontend",
  "sh/14ryd8fq":"以清單、價格狀態、Chart.js 折線圖與成本試算呈現。",
  "sh/6d0fytg3":"資料來源、清洗、資料庫和畫面分開處理，之後才能擴充來源或補足驗證規則。",
  "sh/a5kr2xg3":"ICHIBAN PRICE MONITORING MVP",
  "sh/1cj2d8b6":"三張表，把「追蹤對象、商品刊登、價格歷史」分開保存",
  "sh/0ba143al":"04",
  "sh/ql8jytsj":"tracked_items",
  "sh/doj29oba":"作品、角色、搜尋關鍵字\n與 1–5 分欄位\n啟用追蹤設定",
  "sh/sna103ap":"一個追蹤角色可對應多筆 Rakuten 商品。",
  "sh/ih8ju9sn":"listings",
  "sh/kbm987y5":"商品名稱、URL、圖片\n來源、最後看見時間\nURL 唯一",
  "sh/5cva1cfq":"price_snapshots",
  "sh/jadsz2xk":"日圓價格、運費欄位\n庫存狀態、抓取時間\n保存歷史變化",
  "sh/x8vaxsfe":"關係：tracked_items 1 ──< listings 1 ──< price_snapshots",
  "sh/v6tsv2xo":"實際 schema 只有這三張表；目前沒有 alerts 資料表。",
  "sh/g36tgryd":"設計重點",
  "sh/h4fa9wfy":"不只存最新價格，而是讓同一商品在不同日期的價格可以回看。",
  "sh/oz29krqh":"資料品質",
  "sh/3ytsrmpw":"爬蟲以商品 URL 與日期避免同日重複快照。",
  "sh/2xkrih8b":"限制",
  "sh/1wbapc7q":"Rakuten 為刊登價，不是實際成交價。",
  "sh/sb6xsvu9":"ICHIBAN PRICE MONITORING MVP",
  "sh/dgbulwnm":"資料取得後，先用規則去掉明顯不適合比較的商品",
  "sh/cf2tcr61":"05",
  "sh/z2tcnm5s":"Crawler 實際步驟",
  "sh/yhkbe1o7":"搜尋",
  "sh/l4bupwny":"讀取啟用的 tracked_items，逐一呼叫 Rakuten Item Search API。",
  "sh/n6dcr65o":"解析",
  "sh/m5kbi1oj":"兼容 Items / Item 外層格式與不同圖片欄位，擷取名稱、價格、URL、商店與庫存。",
  "sh/x4vedgvm":"清洗",
  "sh/ahkvi1cb":"排除セット、予約、福袋等字詞，並限制價格範圍。",
  "sh/k7mxovud":"寫入",
  "sh/58vehgvy":"更新 listing 的最後看見時間；同一 listing 同日不重複新增 snapshot。",
  "sh/j6dwfqds":"目前日本國內運費欄位尚未由爬蟲取得，寫入快照時為 NULL；成本試算器由使用者手動輸入。",
  "sh/4f2pgr2h":"ICHIBAN PRICE MONITORING MVP",
  "sh/yhg7epsj":"每日中位數讓單筆極端價格不直接主導整體觀察",
  "sh/zi98nu94":"06",
  "sh/98rqt4r6":"1. 分組",
  "sh/ml07i9sv":"依 captured_at 的日期\n收集同一角色所有快照",
  "sh/oryp8fah":"2. 中位數",
  "sh/pc76hkr2":"Python median()\n產生每日代表價格",
  "sh/h4bupgn6":"避免單筆極端價",
  "sh/v2tcn650":"3. 趨勢",
  "sh/u1kbu1ov":"排序日期後\n交給 Chart.js 畫折線",
  "sh/47mt0b6x":"歷史價格走勢",
  "sh/j6dcr65c":"4. 訊號",
  "sh/i54bylor":"最新日與前一資料日\n中位數上升 ≥15%",
  "sh/qpwnet0b":"潛在漲幅預警",
  "sh/bq547yhw":"單筆相對同日中位數 ≤−15%／≥+15% 顯示低估特價或溢價偏高；資料少於兩天則顯示資料不足。",
  "sh/0fy5k3id":"觀察訊號，不是預測",
  "sh/ydgnit07":"重要限制",
  "sh/zep4byhs":"目前沒有 README 所述的「48 小時」或「樣本至少 5 筆」條件，也沒有預警保存。",
  "sh/1k3mhozu":"報告時誠實說明",
  "sh/jet8nm1c":"不以此規則宣稱可以穩定套利。",
  "sh/25ojml43":"ICHIBAN PRICE MONITORING MVP",
  "sh/cb2tkvap":"成本試算把「日本比較便宜」換成可檢查的保本條件",
  "sh/dcbud0ra":"07",
  "sh/ydkbm5sv":"輸入",
  "sh/kzmdova1":"日圓商品價、國內運費、匯率、代購費、國際運費、平台費與預估售價。",
  "sh/eh0ba1sr":"換算",
  "sh/fi9c369c":"(商品價＋日本運費) × 匯率 → 商品台幣成本；再加代購費與國際運費。",
  "sh/baxkjqlk":"落地成本",
  "sh/xcz2l03q":"扣除",
  "sh/cbq1sv25":"預估售價 × 平台費率；再計算淨利與保本售價。",
  "sh/p8fih03e":"平台費",
  "sh/o761ov2t":"結果依淨利顯示「可觀察／損益兩平／不建議」。",
  "sh/25ojml43":"ICHIBAN PRICE MONITORING MVP",
  "sh/cb2tkvap":"成本試算把「日本比較便宜」換成可檢查的保本條件",
  "sh/dcbud0ra":"07",
  "sh/ydkbm5sv":"輸入",
  "sh/kzmdova1":"日圓商品價、國內運費、匯率、代購費、國際運費、平台費與預估售價。",
  "sh/eh0ba1sr":"換算",
  "sh/fi9c369c":"(商品價＋日本運費) × 匯率 → 商品台幣成本；再加代購費與國際運費。",
  "sh/baxkjqlk":"落地成本",
  "sh/xcz2l03q":"扣除",
  "sh/cbq1sv25":"預估售價 × 平台費率；再計算淨利與保本售價。",
  "sh/p8fih03e":"平台費",
  "sh/o761ov2t":"結果依淨利顯示「可觀察／損益兩平／不建議」。",
  "sh/kfixwbe1":"ICHIBAN PRICE MONITORING MVP",
  "sh/18byd4zy":"Demo：從首頁、角色詳情到成本試算，確認資料如何被使用",
  "sh/g72x4zyd":"08",
  "sh/ri9g7uhw":"Demo 流程",
  "sh/6h0fypgb":"首頁",
  "sh/tkby9kzm":"查看多作品、多角色的最新 listing 與 Rakuten 外連。",
  "sh/je9g3ahk":"角色詳情",
  "sh/id0fu50z":"看分數欄位、每日中位數走勢、單筆狀態和兩日變動訊號。",
  "sh/98rehwve":"提醒",
  "sh/m5gvmhwn":"若真實資料不足兩日，頁面會誠實顯示「資料不足」。",
  "sh/0jydkreh":"成本試算",
  "sh/1k7edwv2":"輸入實際採購假設，從落地成本回推最低保本售價。",
  "sh/zipwbmdc":"此頁使用本機網站截圖；商品和數值僅代表當時畫面，不作為市場結論。",
  "sh/lsn2h4fa":"ICHIBAN PRICE MONITORING MVP",
  "sh/1cfmhgne":"目前已完成一條可展示的 MVP 鏈路，但市場驗證仍在起點",
  "sh/0b65obm9":"09",
  "sh/mdonql4z":"1",
  "sh/9gzml0nq":"單一自動資料來源：Rakuten Item Search API",
  "sh/bih4na5w":"3",
  "sh/ah8nu54b":"3 張實際 schema 資料表：追蹤項目、listing、價格快照",
  "sh/p0ji9kf2":"4",
  "sh/2xsjepgb":"Flask 清單／詳情／成本試算頁，以及 Chart.js 折線圖",
  "sh/cnu1kzyd":"0",
  "sh/do3id4fy":"台灣自動市場資料：目前未實作",
  "sh/bml0buxs":"已完成與限制",
  "sh/0ru1ozyp":"完成：Rakuten 查詢、清洗、去重寫入、每日中位數、簡易變動訊號、成本公式與前端頁面。\n\n限制：刊登價不等於成交價；未驗證穩定套利；無排程、alerts 表、48 小時／樣本數規則、台灣市場比對或 ML。",
  "sh/wvetgbud":"NEXT",
  "sh/xc3mho32":"下一步先補資料可信度，再談更進一步的機會分析",
  "sh/cbu58j2h":"不急著加新名詞；先把目前 MVP 的資料累積、驗證與可追溯性補完整。",
  "sh/zelojyl8":"01",
  "sh/ydcnatkn":"定時累積快照",
  "sh/l036l83y":"加入排程、執行紀錄與失敗通知，累積足夠長的歷史資料。",
  "sh/725onyl4":"02",
  "sh/m1cnetkj":"補台灣資料",
  "sh/s7yt4b21":"建立可比對的台灣售價／成交資料，驗證跨市場假說。",
  "sh/q5gb21kb":"03",
  "sh/r6pcv6lw":"強化預警規則",
  "sh/0bit8b2d":"保存 alerts，加入樣本數、時間窗與資料品質條件。",
  "sh/e9gb61k7":"04",
  "sh/fapcz6ls":"檢驗成本假設",
  "sh/ozitcv29":"用可追溯的匯率、物流與平台費，檢驗保本價是否合理。",
  "sh/xwnupgvy":"10"
};

Object.assign(text, {
  "sh/3ihk3et8":"listings",
  "sh/ih8ju9sn":"商品名稱、URL、圖片\n來源與最後看見時間\n商品 URL 唯一",
  "sh/5cva1cfq":"price_snapshots",
  "sh/i94r6xgz":"每次觀測的日圓價格、可空運費、庫存狀態與抓取時間。",
  "sh/w72947yt":"關係與去重",
  "sh/x8vaxsfe":"tracked_items 1 ──< listings 1 ──< price_snapshots\n爬蟲以 URL 與日期避免重複快照。",
  "sh/50bqpcj2":"解讀時要分開看：每日中位數是整體觀察；單筆商品相對中位數的 ±15% 是價格狀態。兩者都不是成交價或保證獲利。",
  "sh/l0vuh0rm":"換算",
  "sh/n6x0fqlo":"結果只表示輸入條件下的成本試算；預估售價並非系統抓取的市場成交價。",
  "sh/svmt4v6t":"4. 訊號",
  "sh/cbe5g3ih":"最新日與前一資料日\n中位數上升 ≥15%",
  "sh/idk7ehkr":"觀察訊號，不是預測"
});

const textSnapshot = await deck.inspect({kind:"textbox", maxChars:120000});
const editableIds = new Set(textSnapshot.ndjson.split("\n").filter(Boolean).map(line => JSON.parse(line).id));
for (const [id, value] of Object.entries(text)) {
  if (editableIds.has(id)) deck.resolve(id).text = value;
}

const images = {
  1: [`${shot}/螢幕擷取畫面_16-8-2026_124121_127.0.0.1.jpeg`],
  5: [`${shot}/螢幕擷取畫面_16-8-2026_123042_127.0.0.1.jpeg`],
  6: [
    `${shot}/螢幕擷取畫面_16-8-2026_124324_127.0.0.1.jpeg`,
    `${shot}/螢幕擷取畫面_16-8-2026_124539_127.0.0.1.jpeg`,
    `${shot}/螢幕擷取畫面_16-8-2026_124559_127.0.0.1.jpeg`,
    `${shot}/screenshot-1786855416121.png`
  ],
  7: [`${shot}/螢幕擷取畫面_16-8-2026_124539_127.0.0.1.jpeg`],
  8: [`${shot}/螢幕擷取畫面_16-8-2026_124121_127.0.0.1.jpeg`]
};
const snap = await deck.inspect({kind:"image", maxChars:12000});
const imageIndex = {};
for (const line of snap.ndjson.split("\n")) {
  if (!line.trim()) continue;
  const record = JSON.parse(line);
  if (!images[record.slide]) continue;
  const index = imageIndex[record.slide] ?? 0;
  const path = images[record.slide][Math.min(index, images[record.slide].length - 1)];
  imageIndex[record.slide] = index + 1;
  const bytes = await fs.readFile(path);
  const image = deck.resolve(record.id);
  image.replace({blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), contentType: path.endsWith(".png") ? "image/png" : "image/jpeg", alt: "本機網站截圖"});
}

const notes = [
  "建議時間：55 秒\n講稿：今天報告的是台日一番賞價格監測系統。第一階段只接 Rakuten；我們把商品刊登價做成歷史快照，再加上趨勢觀察與跨境成本試算。先說清楚，這是套利可行性分析的 MVP，不保證獲利。\n追問補充：Rakuten 為唯一自動來源，未使用台灣成交價。\n[Sources]\n- Repository: README.md, app.py, crawler/rakuten_crawler.py\n- Local asset: C:/Users/student/Desktop/網頁截圖/螢幕擷取畫面_16-8-2026_124121_127.0.0.1.jpeg",
  "建議時間：80 秒\n講稿：我們發現問題不只是日本商品多，而是同一角色會有很多刊登。單看一筆價格容易失真，也看不到趨勢。即使日本價格較低，把物流與平台費算進去也未必有空間，所以我們把問題拆成價格、趨勢與成本。\n追問補充：本專題不主張已發現台日穩定價差。\n[Sources]\n- Repository: PROJECT_ANALYSIS.md, app.py",
  "建議時間：95 秒\n講稿：這是實作中的資料流程。爬蟲從啟用追蹤角色取得日文關鍵字，向 Rakuten 查詢；清洗後寫入 MySQL，網站再讀資料顯示。這樣每一段可以單獨檢查。\n追問補充：沒有 Docker、排程或 REST JSON API。\n[Sources]\n- Repository: crawler/rakuten_crawler.py, app.py, database.py",
  "建議時間：85 秒\n講稿：資料庫只有三張核心表。tracked_items 是追蹤設定，listings 是實際商品 URL，price_snapshots 是每一次觀測的價格。設計重點是保留價格歷史，而不是覆蓋成最新值。\n追問補充：schema 沒有 alerts 表。\n[Sources]\n- Repository: database/schema.sql",
  "建議時間：85 秒\n講稿：爬蟲實際會解析名稱、價格、URL、圖片、商店與庫存；再排除套組、預購、福袋和異常價格。商品網址被設計為唯一，快照也避免同一天重複寫入。日本國內運費目前並不會被自動抓取。\n追問補充：角色名稱比對仍可再加強。\n[Sources]\n- Repository: crawler/rakuten_crawler.py\n- Local asset: C:/Users/student/Desktop/網頁截圖/螢幕擷取畫面_16-8-2026_123042_127.0.0.1.jpeg",
  "建議時間：105 秒\n講稿：價格分析不是直接取平均，而是把同一角色當天所有快照做中位數，降低單筆極端價影響。兩個資料日以上時，會比較最新與前一日中位數；上升 15% 才顯示潛在漲幅預警。它只是觀察訊號。\n追問補充：程式尚未實作 48 小時與最少五筆樣本規則，預警也沒保存。\n[Sources]\n- Repository: app.py, templates/character_detail.html",
  "建議時間：95 秒\n講稿：成本試算會將商品價格、國內運費、匯率、代購費、國際運費、平台費與預估售價一起計算，得到落地成本、保本售價和預估淨利。這頁展示公式在網站中的實際輸入介面。\n追問補充：所有費率都是使用者假設，預估售價不是系統自動取得。\n[Sources]\n- Repository: app.py, templates/calculator.html\n- Local asset: C:/Users/student/Desktop/網頁截圖/螢幕擷取畫面_16-8-2026_124539_127.0.0.1.jpeg",
  "建議時間：90 秒\n講稿：Demo 時先從首頁點角色，讓老師看最新 listing 與 Rakuten 連結；再看詳情頁的每日中位數、價格狀態與兩日訊號；最後切成本試算器。若資料不足兩日，不要硬講趨勢，直接展示系統的資料不足提示。\n追問補充：截圖為本機網站畫面，不能當市場研究結論。\n[Sources]\n- Repository: templates/index.html, templates/character_detail.html, templates/calculator.html\n- Local asset: C:/Users/student/Desktop/網頁截圖/螢幕擷取畫面_16-8-2026_124121_127.0.0.1.jpeg",
  "建議時間：95 秒\n講稿：到目前為止，從 Rakuten 查詢到網頁呈現的鏈路已經存在。但要誠實說，這不是完成的跨市場套利驗證：缺台灣自動資料、成交價、排程與完整預警保存。\n追問補充：test_data.sql 是本機驗證資料，不是市場成果。\n[Sources]\n- Repository: PROJECT_ANALYSIS.md, database/schema.sql, database/test_data.sql",
  "建議時間：75 秒\n講稿：下一步不是先加機器學習，而是先讓資料更可信。先持續累積快照，補上台灣資料，再把預警變成可保存可檢查的紀錄，最後才檢驗成本假設和跨市場關係。\n追問補充：這樣的優先順序能避免資料不足時做出過度結論。\n[Sources]\n- Repository: PROJECT_ANALYSIS.md"
];
for (let i = 0; i < notes.length; i++) {
  const slide = deck.slides.getItem(i);
  slide.speakerNotes.textFrame.setText(notes[i]);
  slide.speakerNotes.setVisible(true);
}

const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(output);
