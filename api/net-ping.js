export const runtime = 'nodejs';
module.exports = async function handler(req,res){
  try{
    const https = require("https");
    async function head(hostname){
      return await new Promise(resolve=>{
        const req = https.request({hostname, method:"HEAD", path:"/", timeout:5000}, r=>resolve(r.statusCode||0));
        req.on("error",()=>resolve(0)); req.on("timeout",()=>{try{req.destroy()}catch{}; resolve(0)}); req.end();
      });
    }
    const stripe = await head("api.stripe.com");
    const vercel = await head("vercel.com");
    const cloudflare = await head("cloudflare.com");
    return res.status(200).json({ ok:true, stripe, vercel, cloudflare });
  }catch(e){
    return res.status(500).json({ ok:false, error:e?.message });
  }
}
