export const runtime = 'nodejs';
module.exports = async function handler(req,res){
  if (req.method !== "POST") { res.setHeader("Allow","POST"); return res.status(405).json({ ok:false, error:"Method Not Allowed" }); }
  if (!process.env.STRIPE_SECRET_KEY) return res.status(501).json({ ok:false, error:"Stripe non configuré (désactivé)" });
  try{
    const Stripe = require("stripe");
    const stripe = Stripe(process.env.STRIPE_SECRET_KEY,{apiVersion:"2022-11-15"});
    const FRONT=((process.env.FRONTEND_URL||"https://egoejo.vercel.app")+"").trim().replace(/\/+$/,"");
    const session = await stripe.checkout.sessions.create({
      mode:"payment",
      line_items:[{ price_data:{currency:"eur",product_data:{name:"Soutien EGOEJO"},unit_amount:1000}, quantity:1 }],
      success_url:`${FRONT}/?payment=success`, cancel_url:`${FRONT}/?payment=cancel`
    });
    return res.status(200).json({ ok:true, url:session.url });
  }catch(e){ console.error("Stripe error:",e); return res.status(500).json({ ok:false, error:"Stripe error" }); }
}
