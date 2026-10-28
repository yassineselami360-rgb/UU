const $ = id => document.getElementById(id);
const imageInput = $("imageInput");
let selectedFile = null;
let english = false;

function showImage(file) {
  if (!file) return;
  if (!["image/png","image/jpeg","image/webp"].includes(file.type)) {
    $("errorMsg").hidden = false; $("errorMsg").textContent = "اختر صورة بصيغة PNG أو JPG أو WEBP."; return;
  }
  selectedFile = file;
  const url = URL.createObjectURL(file);
  $("imagePreview").src = url; $("imagePreview").hidden = false;
  $("uploadTitle").textContent = file.name;
  $("uploadDesc").textContent = "تم اختيار الصورة — اضغط لتغييرها";
  $("phoneImage").src = url; $("phoneImage").hidden = false;
  $("productPlaceholder").hidden = true;
  $("errorMsg").hidden = true;
}
imageInput.addEventListener("change", e => showImage(e.target.files[0]));
$("dropZone").addEventListener("dragover", e => {e.preventDefault(); $("dropZone").style.borderColor="#b5a2ff";});
$("dropZone").addEventListener("dragleave", () => $("dropZone").style.borderColor="");
$("dropZone").addEventListener("drop", e => {e.preventDefault(); if(e.dataTransfer.files[0]) {imageInput.files=e.dataTransfer.files; showImage(e.dataTransfer.files[0]);}});
$("headline").addEventListener("input", e => $("previewHeadline").textContent=e.target.value || "عنوان إعلانك");
$("subline").addEventListener("input", e => $("previewSubline").textContent=e.target.value || "عبارة تسويقية قصيرة");
$("productName").addEventListener("input", e => { if(! $("headline").dataset.userEdited) { $("headline").value = e.target.value ? "اكتشف " + e.target.value : "اكتشف الفرق بنفسك"; $("previewHeadline").textContent=$("headline").value; }});
$("headline").addEventListener("input", () => $("headline").dataset.userEdited="1");

$("adForm").addEventListener("submit", async e => {
  e.preventDefault();
  if(!selectedFile){$("errorMsg").hidden=false;$("errorMsg").textContent="ارفع صورة المنتج أولاً.";return;}
  $("renderBtn").disabled=true; $("resultCard").hidden=true; $("errorMsg").hidden=true;
  $("progressWrap").hidden=false; $("progressBar").style.width="12%"; $("progressPct").textContent="12%"; $("progressText").textContent="جارٍ تجهيز مشهد المنتج…";
  const form = new FormData();
  form.append("image", selectedFile);
  form.append("headline", $("headline").value);
  form.append("subline", $("subline").value);
  form.append("duration", $("duration").value);
  const stages = [
    [25,"جارٍ إعداد الحركة السينمائية…"],
    [43,"جارٍ معالجة الصورة…"],
    [61,"جارٍ تركيب النصوص…"],
    [78,"جارٍ تصدير ملف MP4…"]
  ];
  let stageIndex=0;
  const ticker=setInterval(()=>{if(stageIndex<stages.length){$("progressBar").style.width=stages[stageIndex][0]+"%";$("progressPct").textContent=stages[stageIndex][0]+"%";$("progressText").textContent=stages[stageIndex][1];stageIndex++;}},1600);
  try {
    const response=await fetch("/api/render",{method:"POST",body:form});
    const data=await response.json();
    if(!response.ok) throw new Error(data.error || "تعذر إنشاء الفيديو.");
    $("progressBar").style.width="100%";$("progressPct").textContent="100%";$("progressText").textContent="اكتمل تصدير الفيديو";
    $("downloadLink").href=data.download_url;
    $("downloadLink").download=data.filename;
    $("resultCard").hidden=false;
  } catch(err) {
    $("errorMsg").hidden=false;
    $("errorMsg").textContent=err.message+" تأكد من تشغيل الخادم وتثبيت FFmpeg.";
  } finally {
    clearInterval(ticker); $("renderBtn").disabled=false;
  }
});

$("langBtn").addEventListener("click",()=>{
  // Lightweight language toggle for the main shell. Core workflow remains usable in Arabic.
  english=!english;
  document.documentElement.lang=english?"en":"ar";
  document.documentElement.dir=english?"ltr":"rtl";
  $("langBtn").textContent=english?"AR / EN":"EN / AR";
  document.querySelector("h1").innerHTML=english?'Turn your product photo into<br><span>an ad that stops the scroll.</span>':'حوّل صورة منتجك إلى<br><span>إعلان يستوقف المشاهد.</span>';
});
