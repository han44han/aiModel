import { supabase } from './database.js';

// الرابط الخاص بسيرفرك على Render (تأكد من تحديثه للرابط الفعلي الخاص بك)
const API_BASE_URL = "https://fixneuro.onrender.com";

// --- 1. التشخيص النصي (يحافظ على المنطق الأصلي) ---
export async function diagnoseText() {
    const textInput = document.getElementById('text-input');
    const resultBox = document.getElementById('result-box');
    const resText = document.getElementById('res-text');
    const mainBtn = document.getElementById('mainBtn');

    if (!textInput || !textInput.value.trim()) {
        alert("يرجى وصف مشكلة السيارة أولاً");
        return;
    }

    // تجهيز الواجهة
    resText.innerHTML = `<p style="color:#4db8ff; text-align:center;">⏳ جاري تحليل العطل نصياً...</p>`;
    resultBox.style.display = 'block';
    mainBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/check`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: textInput.value })
        });
        
        const data = await response.json();
        const isNegative = data.prediction === 'NEGATIVE';

        resText.innerHTML = `
            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-right:5px solid ${isNegative ? '#ff4d4d' : '#4db8ff'};">
                <h3 style="color:${isNegative ? '#ff4d4d' : '#4db8ff'}; margin-bottom:10px;">🔍 نتيجة التحليل النصي</h3>
                <p><strong>حالة العطل:</strong> ${isNegative ? 'تحذير: عطل يحتاج فحص فوري (Severe)' : 'مشكلة بسيطة أو فحص اعتيادي (Minor)'}</p>
                <p style="font-size:13px; color:#aaa; margin-top:10px;">تم التحليل باستخدام نموذج HuggingFace الذكي.</p>
            </div>
        `;
    } catch (error) {
        resText.innerHTML = `<p style="color:#ff4d4d;">❌ تعذر الاتصال بالسيرفر. تأكد من تشغيل App.py</p>`;
    } finally {
        mainBtn.disabled = false;
    }
}

// --- 2. التشخيص بالصور (تحليل مكان الصدمة) ---
export async function diagnoseImage() {
    const imageInput = document.getElementById('image-input');
    const resultBox = document.getElementById('result-box');
    const resText = document.getElementById('res-text');
    const resImg = document.getElementById('res-img');
    const mainBtn = document.getElementById('mainBtn');

    if (!imageInput.files[0]) {
        alert("يرجى اختيار صورة الصدمة أولاً");
        return;
    }

    resText.innerHTML = `<p style="color:#4db8ff; text-align:center;">⏳ جاري فحص الصورة وتحديد مكان الصدمة...</p>`;
    resultBox.style.display = 'block';
    resImg.style.display = 'none';
    mainBtn.disabled = true;

    const formData = new FormData();
    formData.append('carImage', imageInput.files[0]);

    try {
        const response = await fetch(`${API_BASE_URL}/diagnose-image`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        
        if (data.error) throw new Error(data.error);

        const diag = data.diagnosis;

        resText.innerHTML = `
            <div style="background: rgba(255,255,255,0.03); padding:20px; border-radius:15px; border:2px solid ${diag.color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <h3 style="color:${diag.color}; margin:0;">📍 ${diag.location}</h3>
                    <span style="background:${diag.color}; color:#000; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:bold;">الذكاء الاصطناعي</span>
                </div>
                <p style="margin-bottom:10px;"><strong>التشخيص:</strong> ${diag.problem}</p>
                <p style="margin-bottom:15px;"><strong>الحل المقترح:</strong> ${diag.solution}</p>
                <div style="background:rgba(0,0,0,0.4); padding:15px; border-radius:12px; text-align:center; margin-bottom:15px;">
                    <span style="color:#fff; font-size:18px; font-weight:bold;">التكلفة: ${diag.costMin} - ${diag.costMax} ريال</span>
                </div>
                <button onclick="window.location.href='map.html'" style="width:100%; background:${diag.color}; color:#000; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">
                    📍 ابحث عن ورش في ${diag.location}
                </button>
            </div>
        `;

        // عرض معاينة الصورة
        const reader = new FileReader();
        reader.onload = (e) => {
            resImg.src = e.target.result;
            resImg.style.display = 'block';
        };
        reader.readAsDataURL(imageInput.files[0]);

        // حفظ التقرير في سوبابيس
        saveReportToSupabase(diag);

    } catch (error) {
        resText.innerHTML = `<p style="color:#ff4d4d; text-align:center;">❌ فشل تحليل الصورة. (تأكد من تشغيل السيرفر)</p>`;
    } finally {
        mainBtn.disabled = false;
    }
}

// دالة الحفظ
async function saveReportToSupabase(diag) {
    try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
            await supabase.from('maintenance_reports').insert({
                user_id: session.user.id,
                title: `تشخيص: ${diag.location}`,
                description: diag.problem,
                cost: diag.costMax
            });
        }
    } catch (e) { console.log("Database save skipped"); }
}