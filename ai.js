import { supabase } from './database.js';



// الرابط الخاص بسيرفرك على Render

const API_BASE_URL = "https://fixneuro-f6k8.onrender.com";



// --- 1. التشخيص النصي (لم يتم تغيير المنطق كما طلبتِ) ---

export async function startAnalysis() { // تم تغيير الاسم ليتوافق مع استدعاء dia.html

    const textInput = document.getElementById('accidentDescription');

    const resultBox = document.getElementById('resultItems');

    const mainBtn = document.getElementById('mainBtn');



    if (!textInput || !textInput.value.trim()) {

        alert("يرجى وصف مشكلة السيارة أولاً");

        return;

    }



    resultBox.innerHTML = `<p style="color:#4db8ff; text-align:center;">⏳ جاري تحليل العطل نصياً...</p>`;

    resultBox.style.display = 'block';



    try {

        const response = await fetch(`${API_BASE_URL}/check`, {

            method: "POST",

            headers: { "Content-Type": "application/json" },

            body: JSON.stringify({ text: textInput.value })

        });

        

        const data = await response.json();

        const isNegative = data.prediction === 'NEGATIVE';



        resultBox.innerHTML = `

            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; border-right:5px solid ${isNegative ? '#ff4d4d' : '#4db8ff'};">

                <h3 style="color:${isNegative ? '#ff4d4d' : '#4db8ff'}; margin-bottom:10px;">🔍 نتيجة التحليل النصي</h3>

                <p><strong>حالة العطل:</strong> ${isNegative ? 'تحذير: عطل يحتاج فحص فوري (Severe)' : 'مشكلة بسيطة أو فحص اعتيادي (Minor)'}</p>

                <p style="font-size:13px; color:#aaa; margin-top:10px;">تم التحليل باستخدام نموذج HuggingFace الذكي.</p>

            </div>

        `;

    } catch (error) {

        resultBox.innerHTML = `<p style="color:#ff4d4d; text-align:center;">❌ تعذر الاتصال بالسيرفر. تأكدي من تشغيل السيرفر على Render.</p>`;

    }

}



// --- 2. التشخيص بالصور (الربط مع موديل Kaggle/Detectron2) ---

export async function diagnoseImage() {

    const imageInput = document.getElementById('image-input');

    const imageResBox = document.getElementById('image-result-box');

    const imageContent = document.getElementById('image-res-content');

    const imageDisplay = document.getElementById('image-res-display');



    if (!imageInput || !imageInput.files[0]) {

        alert("يرجى رفع صورة أولاً");

        return;

    }



    // تجهيز الواجهة للتحميل

    imageResBox.style.display = 'block';

    imageContent.innerHTML = `<div style="text-align:center; padding:10px;"><p style="color:#4db8ff;">🔍 جاري تحليل الصورة عبر موديل الذكاء الاصطناعي (Detectron2)...</p></div>`;

    imageDisplay.style.display = 'none';



    const formData = new FormData();

    formData.append('file', imageInput.files[0]); // الاسم 'file' يجب أن يطابق ما في app.py



    try {

        const response = await fetch(`${API_BASE_URL}/predict`, {

            method: "POST",

            body: formData

        });

        

        if (!response.ok) throw new Error("Server Error");



        const data = await response.json();

        

        // الحصول على النتيجة من السيرفر (الموديل الخاص بك)

        const rawPrediction = data.prediction || "Clean";

        

        // منطق تحديد الحالة (سليم أم متضرر) بناءً على الكلمة الراجعة

        let predictionLower = rawPrediction.toLowerCase();

        const isSafe = predictionLower.includes("clean") || 

                       predictionLower.includes("no damage") || 

                       predictionLower.includes("سليم");



        let statusColor = isSafe ? "#2ecc71" : "#ff4d4d"; 

        let statusIcon = isSafe ? "✅" : "⚠️";

        let statusTitle = isSafe ? "السيارة سليمة" : "تم رصد ضرر";



        // عرض النتيجة النهائية بشكل جذاب

        imageContent.innerHTML = `

            <div style="padding:15px; border-radius:12px; background:rgba(255,255,255,0.05); border:2px solid ${statusColor};">

                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">

                    <h3 style="color:${statusColor}; margin:0;">📍 نتيجة الفحص البصري:</h3>

                    <span style="background:${statusColor}; color:#000; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:bold;">Kaggle Model</span>

                </div>

                <p style="font-size:18px; font-weight:bold;">${statusIcon} الحالة المكتشفة: ${rawPrediction}</p>

                <p style="font-size:13px; color:#aaa; margin-top:10px;">* تم تحليل هذه الصورة بواسطة خوارزميات الرؤية الحاسوبية المخصصة لـ FixNeuro.</p>

                ${!isSafe ? `<button onclick="window.location.href='map.html'" style="width:100%; margin-top:15px; background:${statusColor}; color:white; border:none; padding:10px; border-radius:8px; cursor:pointer; font-weight:bold;">البحث عن أقرب ورشة إصلاح</button>` : ''}

            </div>`;

        

        // عرض معاينة الصورة التي تم رفعها

        const reader = new FileReader();

        reader.onload = (e) => {

            imageDisplay.src = e.target.result;

            imageDisplay.style.display = 'block';

        };

        reader.readAsDataURL(imageInput.files[0]);



        // اختياري: حفظ التقرير في سوبابيس إذا كان المستخدم مسجلاً

        if (data.status === "success") {

             saveImageReportToSupabase(rawPrediction);

        }



    } catch (error) {

        console.error("Error:", error);

        imageContent.innerHTML = `<p style="color:#ff4d4d; text-align:center;">❌ فشل الاتصال بالسيرفر. تأكدي من رفع ملف app.py على Render وتشغيله.</p>`;

    }

}



// دالة مساعدة لحفظ التقارير

async function saveImageReportToSupabase(prediction) {

    try {

        const { data: { session } } = await supabase.auth.getSession();

        if (session) {

            await supabase.from('maintenance_reports').insert({

                user_id: session.user.id,

                title: `فحص بصري: ${prediction}`,

                description: `تم اكتشاف حالة: ${prediction} عبر تحليل الصورة.`,

                status: 'completed'

            });

        }

    } catch (e) { 

        console.log("Database save skipped or failed"); 

    }

}