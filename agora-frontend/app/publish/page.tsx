"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronRight, ChevronLeft, Rocket } from 'lucide-react';
import confetti from 'canvas-confetti';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function PublishPage() {
  const [step, setStep] = useState(1);
  const [direction, setDirection] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [publishedLoc, setPublishedLoc] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    tagline: '',
    category: 'Research',
    tags: [] as string[],
    status: 'live',
    description: '',
    long_description: '',
    capabilities: [''] as string[],
    input_placeholder: '',
    creator_name: '',
    pricing_model: 'free'
  });

  const [currentTag, setCurrentTag] = useState('');

  const nextStep = () => {
    if (step < 4) {
      setDirection(1);
      setStep(s => s + 1);
    }
  };

  const prevStep = () => {
    if (step > 1) {
      setDirection(-1);
      setStep(s => s - 1);
    }
  };

  const handleCapabilityChange = (index: number, value: string) => {
    const newCaps = [...formData.capabilities];
    newCaps[index] = value;
    setFormData(prev => ({ ...prev, capabilities: newCaps }));
  };

  const addCapability = () => setFormData(prev => ({ ...prev, capabilities: [...prev.capabilities, ''] }));

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const activeCaps = formData.capabilities.filter(c => c.trim().length > 0);
      const res = await api.createAgent({
        ...formData,
        capabilities: activeCaps.length > 0 ? activeCaps : ['Basic execution'],
        tags: formData.tags.length > 0 ? formData.tags : ['ai']
      });
      
      confetti({
        particleCount: 150,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#00F5FF', '#7B2FBE', '#A8FF3E']
      });
      
      setPublishedLoc(`/agent/${res.id}`);
    } catch (err) {
      alert("Failed to publish: " + err);
    }
    setIsSubmitting(false);
  };

  const variants = {
    enter: (direction: number) => ({ x: direction > 0 ? 50 : -50, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit: (direction: number) => ({ x: direction < 0 ? 50 : -50, opacity: 0 })
  };

  if (publishedLoc) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center font-mono container mx-auto px-4 text-center">
        <div className="w-24 h-24 bg-lime/10 border border-lime text-lime rounded-full items-center justify-center flex mb-8">
           <Check className="w-12 h-12" />
        </div>
        <h1 className="font-display text-5xl font-bold text-white mb-4">Your agent is live!</h1>
        <p className="text-muted mb-8 max-w-md">The entity has been successfully registered in the AGORA network and is ready for composition.</p>
        <Link href={publishedLoc}>
           <button className="bg-cyan border border-cyan hover:bg-transparent hover:text-cyan text-void px-8 py-3 font-bold transition-all">VIEW AGENT DASHBOARD</button>
        </Link>
      </div>
    );
  }

  const stepsList = [
    { num: 1, title: 'Identity', desc: 'Name and categorisation' },
    { num: 2, title: 'Description', desc: 'Metadata and capabilities' },
    { num: 3, title: 'Creator', desc: 'Author profile and pricing' },
    { num: 4, title: 'Review', desc: 'Final checks & publish' }
  ];

  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
        {/* LEFT SIDEBAR */}
        <div className="lg:col-span-1">
           <h2 className="font-display font-bold text-2xl text-cyan mb-8">Deploy Agent</h2>
           <div className="space-y-6">
             {stepsList.map(s => (
               <div key={s.num} className={`flex items-start gap-4 ${step === s.num ? 'opacity-100' : step > s.num ? 'opacity-50' : 'opacity-30'}`}>
                 <div className={`w-8 h-8 rounded-full border flex items-center justify-center font-mono text-sm flex-shrink-0 transition-colors ${step === s.num ? 'border-cyan text-cyan bg-cyan/10 box-shadow-glow' : step > s.num ? 'border-lime text-lime bg-lime/10' : 'border-border text-muted bg-elevated'}`}>
                   {step > s.num ? <Check className="w-4 h-4" /> : s.num}
                 </div>
                 <div>
                   <h3 className={`font-bold font-mono text-sm ${step === s.num ? 'text-primary' : 'text-muted'}`}>{s.title}</h3>
                   <p className="text-xs text-dim mt-1">{s.desc}</p>
                 </div>
               </div>
             ))}
           </div>
        </div>

        {/* RIGHT CONTENT */}
        <div className="lg:col-span-3 bg-card border border-border p-8 min-h-[600px] flex flex-col overflow-hidden relative">
           <AnimatePresence custom={direction} mode="wait">
             {step === 1 && (
               <motion.div key="1" custom={direction} variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="flex-1">
                 <h3 className="font-display text-2xl font-bold mb-6 text-primary border-b border-border pb-4">Agent Identity</h3>
                 
                 <div className="space-y-6 max-w-xl">
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">AGENT_NAME</label>
                     <input type="text" maxLength={40} className="w-full bg-elevated border border-border p-3 text-white font-mono focus:border-cyan focus:outline-none" placeholder="e.g. Synthetix-v2" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
                   </div>
                   
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">TAGLINE (Max 120 chars)</label>
                     <input type="text" maxLength={120} className="w-full bg-elevated border border-border p-3 text-white focus:border-cyan focus:outline-none" placeholder="Brief pitch line..." value={formData.tagline} onChange={e => setFormData({...formData, tagline: e.target.value})} />
                   </div>

                   <div className="grid grid-cols-2 gap-6">
                     <div>
                       <label className="block font-mono text-sm text-cyan mb-2">CATEGORY</label>
                       <select className="w-full bg-elevated border border-border p-3 text-white focus:border-cyan focus:outline-none" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})}>
                         {['Research', 'Developer Tools', 'Creative', 'Business', 'Analytics', 'Automation', 'Other'].map(c => (
                           <option key={c} value={c}>{c}</option>
                         ))}
                       </select>
                     </div>
                     <div>
                       <label className="block font-mono text-sm text-cyan mb-2">STATUS</label>
                       <div className="flex gap-4 p-3 bg-elevated border border-border">
                         <label className="flex items-center gap-2 cursor-pointer font-mono text-sm"><input type="radio" checked={formData.status === 'live'} onChange={() => setFormData({...formData, status: 'live'})}/> Live</label>
                         <label className="flex items-center gap-2 cursor-pointer font-mono text-sm text-orange"><input type="radio" checked={formData.status === 'beta'} onChange={() => setFormData({...formData, status: 'beta'})}/> Beta</label>
                       </div>
                     </div>
                   </div>

                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">TAGS (Press Enter)</label>
                     <div className="w-full bg-elevated border border-border p-2 flex flex-wrap gap-2 focus-within:border-cyan transition-colors">
                       {formData.tags.map((t, i) => (
                         <span key={i} className="bg-cyan/10 border border-cyan/30 text-cyan text-xs font-mono px-2 py-1 flex items-center gap-1">
                           {t} <button onClick={() => setFormData(p => ({...p, tags: p.tags.filter((_, idx) => idx !== i)}))} className="hover:text-red-500">×</button>
                         </span>
                       ))}
                       <input type="text" className="bg-transparent border-none focus:outline-none text-white text-sm flex-1 min-w-[100px]" value={currentTag} onChange={e => setCurrentTag(e.target.value)} onKeyDown={(e) => {
                         if (e.key === 'Enter' && currentTag.trim() && formData.tags.length < 6) {
                           e.preventDefault();
                           setFormData(p => ({...p, tags: [...p.tags, currentTag.trim()]}));
                           setCurrentTag('');
                         }
                       }} placeholder={formData.tags.length < 6 ? "Type & enter..." : "Max 6 tags reached"} disabled={formData.tags.length >= 6} />
                     </div>
                   </div>
                 </div>
               </motion.div>
             )}

             {step === 2 && (
               <motion.div key="2" custom={direction} variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="flex-1 overflow-y-auto pr-2 no-scrollbar">
                 <h3 className="font-display text-2xl font-bold mb-6 text-primary border-b border-border pb-4">Core Implementation</h3>
                 
                 <div className="space-y-6 max-w-2xl">
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">SHORT DESCRIPTION</label>
                     <textarea maxLength={200} className="w-full h-24 bg-elevated border border-border p-3 text-white focus:border-cyan focus:outline-none resize-none" placeholder="Appears in marketplace cards..." value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
                   </div>
                   
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">LONG DESCRIPTION (Markdown)</label>
                     <textarea className="w-full h-40 bg-elevated border border-border p-3 text-white focus:border-cyan focus:outline-none font-mono text-sm p-4" placeholder="# How it works..." value={formData.long_description} onChange={e => setFormData({...formData, long_description: e.target.value})} />
                   </div>

                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">PIPELINE CAPABILITIES</label>
                     <div className="space-y-2 mb-2">
                       {formData.capabilities.map((cap, i) => (
                         <div key={i} className="flex gap-2">
                           <input type="text" className="flex-1 bg-elevated border border-border p-2 text-sm text-white focus:border-cyan focus:outline-none font-mono" placeholder={`Capability ${i+1}`} value={cap} onChange={e => handleCapabilityChange(i, e.target.value)} />
                           {formData.capabilities.length > 1 && (
                             <button onClick={() => setFormData(p => ({...p, capabilities: p.capabilities.filter((_, idx) => idx !== i)}))} className="px-3 border border-border bg-void text-muted hover:text-red-500 hover:border-red-500">×</button>
                           )}
                         </div>
                       ))}
                     </div>
                     <button onClick={addCapability} className="text-xs font-mono text-cyan hover:text-white transition-colors">+ Add Capability</button>
                   </div>
                   
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">SANDBOX INPUT PLACEHOLDER</label>
                     <textarea className="w-full h-20 bg-elevated border border-border p-3 text-white focus:border-cyan font-mono text-xs focus:outline-none resize-none" placeholder="Default prompt visible in run terminal..." value={formData.input_placeholder} onChange={e => setFormData({...formData, input_placeholder: e.target.value})} />
                   </div>
                 </div>
               </motion.div>
             )}

             {step === 3 && (
               <motion.div key="3" custom={direction} variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="flex-1">
                 <h3 className="font-display text-2xl font-bold mb-6 text-primary border-b border-border pb-4">Creator Profile</h3>
                 
                 <div className="space-y-6 max-w-xl">
                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">YOUR HANDLE</label>
                     <input type="text" className="w-full bg-elevated border border-border p-3 text-white focus:border-cyan focus:outline-none" placeholder="e.g. @0xDeveloper" value={formData.creator_name} onChange={e => setFormData({...formData, creator_name: e.target.value})} />
                   </div>

                   <div>
                     <label className="block font-mono text-sm text-cyan mb-2">AUTHORISATION & PRICING</label>
                     <div className="grid grid-cols-2 gap-4">
                       <label className={`cursor-pointer border p-4 flex flex-col items-center justify-center transition-all ${formData.pricing_model === 'free' ? 'border-cyan bg-cyan/5 text-cyan' : 'border-border bg-elevated text-muted'}`}>
                         <input type="radio" className="hidden" checked={formData.pricing_model === 'free'} onChange={() => setFormData({...formData, pricing_model: 'free'})}/>
                         <span className="font-display text-2xl font-bold mb-1">FREE</span>
                         <span className="font-mono text-xs">Public execution</span>
                       </label>
                       <label className={`cursor-pointer border p-4 flex flex-col items-center justify-center opacity-50 transition-all ${formData.pricing_model === 'paid' ? 'border-purple bg-purple/5 text-purple' : 'border-border bg-elevated text-muted'}`}>
                         <input type="radio" disabled className="hidden" checked={formData.pricing_model === 'paid'} onChange={() => setFormData({...formData, pricing_model: 'paid'})}/>
                         <span className="font-display text-2xl font-bold mb-1 border-b border-dashed border-current pb-1">PAID</span>
                         <span className="font-mono text-xs">Coming Soon</span>
                       </label>
                     </div>
                   </div>
                 </div>
               </motion.div>
             )}

             {step === 4 && (
               <motion.div key="4" custom={direction} variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="flex-1">
                 <h3 className="font-display text-2xl font-bold mb-6 text-primary border-b border-border pb-4">Pre-Flight Check</h3>

                 <div className="bg-void border border-border p-6 mb-8 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                   <div className="text-xs font-mono text-muted mb-4 pb-2 border-b border-border/50">PREVIEW RENDER</div>
                   <div className="flex gap-4 items-center">
                     <div className="w-16 h-16 bg-elevated border border-cyan/30 flex items-center justify-center flex-shrink-0">
                       <span className="font-display font-bold text-3xl text-cyan">{formData.name ? formData.name.charAt(0) : '?'}</span>
                     </div>
                     <div>
                       <h3 className="font-mono text-xl text-primary">{formData.name || 'Unnamed Agent'}</h3>
                       <div className="text-xs text-muted mt-1 italic">{formData.tagline || 'No tagline provided.'}</div>
                       <div className="flex gap-2 mt-2">
                         <span className="px-2 py-0.5 bg-elevated border border-border text-[10px] font-mono text-cyan uppercase">{formData.category}</span>
                         <span className={`px-2 py-0.5 bg-elevated border text-[10px] font-mono uppercase ${formData.status === 'live' ? 'text-lime border-lime' : 'text-orange border-orange'}`}>{formData.status}</span>
                       </div>
                     </div>
                   </div>
                 </div>

                 <div className="grid grid-cols-2 gap-4 text-sm font-mono mb-8">
                   <div className="border border-border p-4 bg-elevated flex flex-col gap-1">
                     <span className="text-dim text-xs">CREATOR</span>
                     <span className="text-primary">{formData.creator_name || 'Anonymous'}</span>
                   </div>
                   <div className="border border-border p-4 bg-elevated flex flex-col gap-1">
                     <span className="text-dim text-xs">TAGS DETECTED</span>
                     <span className="text-cyan">{formData.tags.length} Active Vectors</span>
                   </div>
                 </div>

                 <p className="text-xs text-dim italic mb-4">By executing deployment, you agree that your logic will be permanently indexed into the AGORA registry and execute safely inside secure VM containers.</p>
               </motion.div>
             )}
           </AnimatePresence>
           
           <div className="mt-8 pt-4 border-t border-border flex justify-between">
             <button onClick={prevStep} disabled={step === 1 || isSubmitting} className="flex items-center gap-2 px-6 py-2 border border-border bg-elevated text-primary font-mono text-sm hover:border-muted disabled:opacity-50 transition-colors">
                <ChevronLeft className="w-4 h-4" /> BACK
             </button>
             
             {step < 4 ? (
               <button onClick={nextStep} className="flex items-center gap-2 px-8 py-2 border border-cyan bg-cyan/10 text-cyan font-mono text-sm hover:bg-cyan hover:text-void font-bold transition-colors">
                  CONTINUE <ChevronRight className="w-4 h-4" />
               </button>
             ) : (
               <button onClick={handleSubmit} disabled={isSubmitting} className="flex items-center gap-2 px-8 py-2 border border-lime bg-lime text-void font-bold font-mono text-sm hover:bg-transparent hover:text-lime transition-all disabled:opacity-50 group relative overflow-hidden">
                  <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform" />
                  {isSubmitting ? <><div className="w-4 h-4 rounded-full border-2 border-t-transparent border-void animate-spin" /> ESTABLISHING LINK...</> : <><Rocket className="w-4 h-4" /> DEPLOY TO AGORA</>}
               </button>
             )}
           </div>
        </div>
      </div>
    </div>
  );
}
