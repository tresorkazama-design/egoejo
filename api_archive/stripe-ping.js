export const runtime = 'nodejs';
module.exports = async function handler(req,res){
  try{
    const key = process.env.STRIPE_SECRET_KEY;
    if(!key) return res.status(500).json({ok:false,error:"Stripe non configuré"});
    const https = require("https");
    const status = await new Promise((resolve) => {
      const rq = https.request({ hostname:"api.stripe.com", path:"/", method:"GET", timeout:5000 }, r=>resolve(r.statusCode||0));
      rq.on("error", ()=>resolve(0)); rq.on("timeout",()=>{try{rq.destroy()}catch{}; resolve(0)}); rq.end();
    });
    const Stripe = require("stripe");
    const stripe = Stripe(key,{apiVersion:"2022-11-15"});
    const prices = await stripe.prices.list({limit:1});
    return res.status(200).json({ ok:true, networkStatus: status, mode: key.startsWith("sk_live_")?"live":"test", sample_price: prices.data?.[0]?.id||null });
  }catch(e){
    return res.status(500).json({ ok:false, error:e.message, code:e.code, type:e.type });
  }
}
