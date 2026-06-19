import tkinter as tk
from tkinter import ttk


def trimf(x, a, b, c):
    if x <= a or x >= c: return 0.0
    return (x-a)/(b-a) if x <= b else (c-x)/(c-b)

def zmf(x, a, b):
    if x <= a: return 1.0
    if x >= b: return 0.0
    return (b-x)/(b-a)

def smf(x, a, b):
    if x <= a: return 0.0
    if x >= b: return 1.0
    return (x-a)/(b-a)

def fz_umur(u):
    # Muda: <30, ParuhBaya: 25-60, Tua: >50
    return {"Muda": zmf(u,25,40), "ParuhBaya": trimf(u,30,45,60), "Tua": smf(u,50,65)}

def fz_bmi(b):
    # Standar Asia-Pasifik: Normal<23, Overweight 23-27, Obesitas >27
    return {"Normal": zmf(b,18,25), "Overweight": trimf(b,22,27,32), "Obesitas": smf(b,27,37)}

def fz_gula(g):
    # ADA: Normal <100-126, Prediabetes 100-199, Diabetes >=160+
    return {"Normal": zmf(g,90,130), "Prediabetes": trimf(g,100,150,200), "Diabetes": smf(g,160,220)}

def fz_aktiv(a):
    # Rendah: <30, Sedang: 20-70, Tinggi: >60
    return {"Rendah": zmf(a,15,40), "Sedang": trimf(a,25,52,75), "Tinggi": smf(a,60,80)}

RULES = [
    (lambda u,b,g,a: min(b["Normal"],g["Normal"]),                   "Rendah","IF BMI Normal AND Gula Normal THEN Rendah"),
    (lambda u,b,g,a: min(b["Normal"],g["Prediabetes"]),              "Sedang","IF BMI Normal AND Gula Prediabetes THEN Sedang"),
    (lambda u,b,g,a: min(b["Normal"],g["Diabetes"]),                 "Tinggi","IF BMI Normal AND Gula Diabetes THEN Tinggi"),
    (lambda u,b,g,a: min(b["Overweight"],g["Normal"]),               "Sedang","IF BMI Overweight AND Gula Normal THEN Sedang"),
    (lambda u,b,g,a: min(b["Overweight"],g["Prediabetes"]),          "Sedang","IF BMI Overweight AND Gula Prediabetes THEN Sedang"),
    (lambda u,b,g,a: min(b["Overweight"],g["Diabetes"]),             "Tinggi","IF BMI Overweight AND Gula Diabetes THEN Tinggi"),
    (lambda u,b,g,a: min(b["Obesitas"],g["Normal"]),                 "Sedang","IF BMI Obesitas AND Gula Normal THEN Sedang"),
    (lambda u,b,g,a: min(b["Obesitas"],g["Prediabetes"]),            "Tinggi","IF BMI Obesitas AND Gula Prediabetes THEN Tinggi"),
    (lambda u,b,g,a: min(b["Obesitas"],g["Diabetes"]),               "Tinggi","IF BMI Obesitas AND Gula Diabetes THEN Tinggi"),
    (lambda u,b,g,a: min(u["Tua"],a["Rendah"]),                      "Tinggi","IF Umur Tua AND Aktivitas Rendah THEN Tinggi"),
    (lambda u,b,g,a: min(u["Tua"],b["Obesitas"]),                    "Tinggi","IF Umur Tua AND BMI Obesitas THEN Tinggi"),
    (lambda u,b,g,a: min(b["Obesitas"],a["Rendah"]),                 "Tinggi","IF BMI Obesitas AND Aktivitas Rendah THEN Tinggi"),
    (lambda u,b,g,a: min(u["Tua"],g["Diabetes"]),                    "Tinggi","IF Umur Tua AND Gula Diabetes THEN Tinggi"),
    (lambda u,b,g,a: min(u["Muda"],b["Normal"],a["Tinggi"]),         "Rendah","IF Umur Muda AND BMI Normal AND Aktivitas Tinggi THEN Rendah"),
    (lambda u,b,g,a: min(a["Tinggi"],g["Normal"]),                   "Rendah","IF Aktivitas Tinggi AND Gula Normal THEN Rendah"),
    (lambda u,b,g,a: min(u["ParuhBaya"],g["Prediabetes"],a["Sedang"]),"Sedang","IF Umur ParuhBaya AND Gula Prediabetes AND Aktivitas Sedang THEN Sedang"),
]

def mf_R(x): return trimf(x,0,20,40)
def mf_S(x): return trimf(x,30,50,70)
def mf_T(x): return trimf(x,60,80,100)

def inferensi(umur, bmi, gula, aktiv):
    u=fz_umur(umur); b=fz_bmi(bmi); g=fz_gula(gula); a=fz_aktiv(aktiv)
    aR=aS=aT=0.0; rule_detail=[]
    for cond,out,desc in RULES:
        alpha=cond(u,b,g,a)
        if out=="Rendah": aR=max(aR,alpha)
        elif out=="Sedang": aS=max(aS,alpha)
        else: aT=max(aT,alpha)
        rule_detail.append((alpha,out,desc))
    return aR,aS,aT,rule_detail

def defuzz_detail(aR, aS, aT, n=500):
    num=den=0.0
    points=[]
    for k in range(n+1):
        x=k/n*100
        mu=max(min(aR,mf_R(x)),min(aS,mf_S(x)),min(aT,mf_T(x)))
        num+=x*mu; den+=mu
        points.append((x,mu))
    crisp=0.0 if den==0 else num/den
    return crisp, num, den, points

def hitung(umur, bmi, gula, aktiv):
    aR,aS,aT,rule_detail=inferensi(umur,bmi,gula,aktiv)
    crisp,num,den,pts=defuzz_detail(aR,aS,aT)
    label="TINGGI" if crisp>=60 else ("SEDANG" if crisp>=35 else "RENDAH")
    active=[r for r in rule_detail if r[0]>0.001]
    return dict(crisp=crisp,label=label,aR=aR,aS=aS,aT=aT,
                rules=sorted(active,key=lambda x:-x[0]),
                all_rules=rule_detail,
                num=num,den=den,pts=pts,
                fz_u=fz_umur(umur),fz_b=fz_bmi(bmi),
                fz_g=fz_gula(gula),fz_a=fz_aktiv(aktiv))


BG=     "#F1F4F9"
CARD=   "#FFFFFF"
BORDER= "#DDE3EC"
CANVAS= "#F7FAFD"
T1=     "#1A2733"
T2=     "#5B7A91"
T3=     "#A8BBC9"
BLUE=   "#1260CC"
BLUE_L= "#A8C4F0"
CR,CS,CT     = "#16A85A","#E07B10","#D93535"
FR,FS,FT     = "#E6F7EE","#FEF3E6","#FDEAEA"
FR2,FS2,FT2  = "#B4E4CB","#FAD4A0","#F5AEAE"
MONO=   ("Courier New",9)
MONOB=  ("Courier New",9,"bold")
SANS=   ("Helvetica",9)
SANSB=  ("Helvetica",9,"bold")
SANSS=  ("Helvetica",8)


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Sistem Penentuan Risiko Diabetes — Fuzzy Mamdani")
        self.configure(bg=BG)
        try: self.state("zoomed")
        except: self.geometry("1400x860")

        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=0)
        self.columnconfigure(0,weight=1)

        self._topbar()

        nb_frame = tk.Frame(self, bg=BG)
        nb_frame.grid(row=1,column=0,sticky="nsew",padx=12,pady=(8,4))
        nb_frame.rowconfigure(0,weight=1)
        nb_frame.columnconfigure(0,weight=1)

        style=ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",background=BG,borderwidth=0,tabmargins=0)
        style.configure("TNotebook.Tab",background="#DDE3EC",foreground=T2,
                        font=("Helvetica",9,"bold"),padding=[14,6])
        style.map("TNotebook.Tab",
                  background=[("selected",CARD)],
                  foreground=[("selected",BLUE)])

        self.nb = ttk.Notebook(nb_frame)
        self.nb.grid(row=0,column=0,sticky="nsew")

        t1=tk.Frame(self.nb,bg=BG); self.nb.add(t1,text="  Dashboard  ")
        self._build_dashboard(t1)

        t2=tk.Frame(self.nb,bg=BG); self.nb.add(t2,text="  Fungsi Keanggotaan  ")
        self._build_mf_tab(t2)

        t3=tk.Frame(self.nb,bg=BG); self.nb.add(t3,text="  Perhitungan Manual  ")
        self._build_manual_tab(t3)


        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._interpretasi()
        self.after(200,self._hitung)

    def _is_manual_tab_active(self):
        try:
            return self.nb.tab(self.nb.select(),"text").strip()=="Perhitungan Manual"
        except Exception:
            return False

    def _on_tab_changed(self,event=None):
        if self._is_manual_tab_active():
            self._build_manual_content()

    @staticmethod
    def _card(p,**kw):
        return tk.Frame(p,bg=CARD,highlightthickness=1,
                        highlightbackground=BORDER,**kw)

    @staticmethod
    def _sep(p,py=4):
        tk.Frame(p,bg=BORDER,height=1).pack(fill="x",pady=py)

    @staticmethod
    def _hdr(p,text,sub=None,color=None):
        row=tk.Frame(p,bg=p["bg"]); row.pack(fill="x",pady=(0,6))
        tk.Frame(row,bg=color or BLUE,width=3,height=15).pack(side="left",padx=(0,8))
        tk.Label(row,text=text,font=SANSB,bg=p["bg"],fg=T1).pack(side="left")
        if sub:
            tk.Label(row,text=f"  {sub}",font=SANSS,bg=p["bg"],fg=T3).pack(side="left",pady=(2,0))

    def _topbar(self):
        tb=tk.Frame(self,bg=CARD,height=46,
                    highlightthickness=1,highlightbackground=BORDER)
        tb.grid(row=0,column=0,sticky="ew"); tb.pack_propagate(False)
        tk.Label(tb,text="⬤",font=("Helvetica",13),bg=CARD,fg=BLUE
                 ).pack(side="left",padx=(16,8))
        tk.Label(tb,text="SKRINING RISIKO DIABETES",
                 font=("Helvetica",12,"bold"),bg=CARD,fg=T1).pack(side="left")
        tk.Label(tb,text="   Fuzzy Mamdani  ·  Defuzzifikasi Centroid",
                 font=SANSS,bg=CARD,fg=T2).pack(side="left",pady=(2,0))

    def _build_dashboard(self, parent):
        parent.columnconfigure(0,weight=0,minsize=270)
        parent.columnconfigure(1,weight=0,minsize=210)
        parent.columnconfigure(2,weight=1)
        parent.columnconfigure(3,weight=0,minsize=310)
        parent.rowconfigure(0,weight=1)

        self._sidebar(parent)
        self._result_col(parent)
        self._charts_col(parent)
        self._rules_col(parent)

    def _sidebar(self,parent):
        col=tk.Frame(parent,bg=BG)
        col.grid(row=0,column=0,sticky="nsew",padx=(8,10),pady=8)

        ic=self._card(col); ic.pack(fill="x",pady=(0,8))
        ii=tk.Frame(ic,bg=CARD,padx=14,pady=12); ii.pack(fill="x")
        self._hdr(ii,"Data Pasien")
        self._sep(ii,3)

        self.v_umur =tk.DoubleVar(value=52)
        self.v_bmi  =tk.DoubleVar(value=29.0)
        self.v_gula =tk.DoubleVar(value=175)
        self.v_aktiv=tk.DoubleVar(value=35)

        self._slider(ii,"Umur  (10 – 80 tahun)",
                     self.v_umur,10,80,lambda v:f"{int(v)} tahun")
        self._sep(ii,3)
        self._slider(ii,"BMI  (10.0 – 50.0 kg/m²)",
                     self.v_bmi,10,50,lambda v:f"{v:.1f} kg/m²",step=0.1)
        self._sep(ii,3)
        self._slider(ii,"Gula Darah  (70 – 300 mg/dL)",
                     self.v_gula,70,300,lambda v:f"{int(v)} mg/dL")
        self._sep(ii,3)
        self._slider(ii,"Aktivitas Fisik  (0 – 100)",
                     self.v_aktiv,0,100,lambda v:f"{int(v)} / 100")
        self._sep(ii,7)
        tk.Button(ii,text="▶   Hitung Risiko Diabetes",
                  font=SANSB,bg=BLUE,fg="white",relief="flat",
                  cursor="hand2",padx=10,pady=9,
                  activebackground="#0E4FAA",activeforeground="white",
                  command=self._hitung).pack(fill="x")

        fc=self._card(col); fc.pack(fill="x")
        fi=tk.Frame(fc,bg=CARD,padx=14,pady=10); fi.pack(fill="x")
        self._hdr(fi,"Nilai Fuzzifikasi")
        self._sep(fi,3)
        self.fuzz_frame=tk.Frame(fi,bg=CARD); self.fuzz_frame.pack(fill="x")

    def _result_col(self,parent):
        col=tk.Frame(parent,bg=BG)
        col.grid(row=0,column=1,sticky="nsew",padx=(0,10),pady=8)
        col.rowconfigure(0,weight=0); col.rowconfigure(1,weight=1)
        col.columnconfigure(0,weight=1)

        rc=self._card(col); rc.grid(row=0,column=0,sticky="ew",pady=(0,8))
        ri=tk.Frame(rc,bg=CARD,padx=16,pady=14); ri.pack(fill="x")
        tk.Label(ri,text="HASIL RISIKO",font=("Helvetica",8,"bold"),
                 bg=CARD,fg=T3).pack()
        self.lbl_hasil=tk.Label(ri,text="—",font=("Helvetica",28,"bold"),
                                bg=CARD,fg=T3); self.lbl_hasil.pack(pady=(2,0))
        self.lbl_crisp=tk.Label(ri,text="Nilai crisp: —",font=MONO,
                                bg=CARD,fg=T2); self.lbl_crisp.pack(pady=(0,8))
        tk.Label(ri,text="Skor Risiko  (0 – 100)",font=("Helvetica",7),
                 bg=CARD,fg=T3).pack(anchor="w")
        self.gauge=tk.Canvas(ri,bg=CARD,height=22,highlightthickness=0)
        self.gauge.pack(fill="x",pady=(2,0))
        self.gauge.bind("<Configure>",
            lambda e:self._draw_gauge(getattr(self,"_crisp",0),
                                      getattr(self,"_label","RENDAH")))

        ac=self._card(col); ac.grid(row=1,column=0,sticky="nsew")
        ai=tk.Frame(ac,bg=CARD,padx=14,pady=14); ai.pack(fill="both",expand=True)
        self._hdr(ai,"Nilai Alpha (α)")
        self._sep(ai,4)
        self.abars={}; self.avals={}
        for name,col_c in [("Rendah",CR),("Sedang",CS),("Tinggi",CT)]:
            rw=tk.Frame(ai,bg=CARD); rw.pack(fill="x",pady=6)
            dn=tk.Frame(rw,bg=CARD); dn.pack(fill="x")
            tk.Frame(dn,bg=col_c,width=10,height=10).pack(side="left",pady=2)
            tk.Label(dn,text=f"  {name}",font=SANSB,bg=CARD,fg=col_c).pack(side="left")
            lv=tk.Label(dn,text="0.000",font=MONOB,bg=CARD,fg=col_c)
            lv.pack(side="right"); self.avals[name]=lv
            tr=tk.Frame(rw,bg="#E4EBF5",height=10); tr.pack(fill="x",pady=(3,0))
            fl=tk.Frame(tr,bg=col_c,height=10,width=0); fl.place(x=0,y=0,relheight=1)
            self.abars[name]=(tr,fl)

    def _charts_col(self,parent):
        col=tk.Frame(parent,bg=BG)
        col.grid(row=0,column=2,sticky="nsew",padx=(0,10),pady=8)
        col.rowconfigure(0,weight=1); col.rowconfigure(1,weight=1)
        col.columnconfigure(0,weight=1)

        mc=self._card(col); mc.grid(row=0,column=0,sticky="nsew",pady=(0,8))
        mi=tk.Frame(mc,bg=CARD,padx=12,pady=10); mi.pack(fill="both",expand=True)
        self._hdr(mi,"Fungsi Keanggotaan Output")
        self._legend(mi,[("Rendah",CR),("Sedang",CS),("Tinggi",CT)])
        self.cmf=tk.Canvas(mi,bg=CANVAS,highlightthickness=1,highlightbackground=BORDER)
        self.cmf.pack(fill="both",expand=True)

        agc=self._card(col); agc.grid(row=1,column=0,sticky="nsew")
        agi=tk.Frame(agc,bg=CARD,padx=12,pady=10); agi.pack(fill="both",expand=True)
        self._hdr(agi,"Agregasi & Defuzzifikasi")
        self._legend(agi,[("Rendah",CR),("Sedang",CS),("Tinggi",CT)],centroid=True)
        self.cagg=tk.Canvas(agi,bg=CANVAS,highlightthickness=1,highlightbackground=BORDER)
        self.cagg.pack(fill="both",expand=True)

    def _legend(self,p,items,centroid=False):
        lg=tk.Frame(p,bg=CARD); lg.pack(fill="x",pady=(0,4))
        for n,c in items:
            tk.Frame(lg,bg=c,width=11,height=11).pack(side="left",padx=(0,3))
            tk.Label(lg,text=n,font=SANSS,bg=CARD,fg=T2).pack(side="left",padx=(0,12))
        if centroid:
            tk.Frame(lg,bg=BLUE,width=2,height=14).pack(side="left",padx=(4,3))
            tk.Label(lg,text="Centroid",font=SANSS,bg=CARD,fg=T2).pack(side="left")


    def _rules_col(self,parent):
        col=tk.Frame(parent,bg=BG)
        col.grid(row=0,column=3,sticky="nsew",padx=(0,8),pady=8)
        col.rowconfigure(0,weight=1); col.columnconfigure(0,weight=1)

        card=self._card(col); card.grid(row=0,column=0,sticky="nsew")
        inner=tk.Frame(card,bg=CARD,padx=14,pady=14); inner.pack(fill="both",expand=True)
        self._hdr(inner,"Rules Aktif",sub="— α > 0.001, diurutkan tertinggi")
        self._sep(inner,5)

        w=tk.Frame(inner,bg=CARD); w.pack(fill="both",expand=True)
        sb=tk.Scrollbar(w,troughcolor="#EEF2F7",relief="flat",width=8)
        sb.pack(side="right",fill="y")

        self.rtxt=tk.Text(w,font=("Courier New",8),bg=CANVAS,fg=T1,
                          relief="flat",wrap="char",padx=8,pady=6,
                          state="disabled",spacing3=4,yscrollcommand=sb.set)
        self.rtxt.pack(fill="both",expand=True)
        sb.config(command=self.rtxt.yview)
        for tag,col_c,bold in [("num",T3,False),("alpha",BLUE,True),
                                ("rendah",CR,True),("sedang",CS,True),
                                ("tinggi",CT,True),("desc",T2,False)]:
            self.rtxt.tag_config(tag,foreground=col_c,
                                 font=("Courier New",8,"bold" if bold else "normal"))

    def _build_mf_tab(self, parent):
        parent.columnconfigure(0,weight=1); parent.columnconfigure(1,weight=1)
        parent.rowconfigure(0,weight=1); parent.rowconfigure(1,weight=1)

        specs = [
            ("Umur (tahun)",  10,  80,  [("Muda",zmf,25,40,None,CR),("ParuhBaya",trimf,30,45,60,CS),("Tua",smf,50,65,None,CT)],   0,0,"umur"),
            ("BMI (kg/m²)",   10,  50,  [("Normal",zmf,18,25,None,CR),("Overweight",trimf,22,27,32,CS),("Obesitas",smf,27,37,None,CT)], 0,1,"bmi"),
            ("Gula (mg/dL)",  70, 300,  [("Normal",zmf,90,130,None,CR),("Prediabetes",trimf,100,150,200,CS),("Diabetes",smf,160,220,None,CT)], 1,0,"gula"),
            ("Aktivitas (0-100)", 0,100,[("Rendah",zmf,15,40,None,CT),("Sedang",trimf,25,52,75,CS),("Tinggi",smf,60,80,None,CR)], 1,1,"aktiv"),
        ]

        self.mf_canvases = []
        for title,lo,hi,mfs,row,col,var_key in specs:
            card=self._card(parent)
            card.grid(row=row,column=col,sticky="nsew",padx=(8 if col==0 else 4, 4 if col==0 else 8),
                      pady=(8 if row==0 else 4, 4 if row==0 else 8))
            inner=tk.Frame(card,bg=CARD,padx=12,pady=10); inner.pack(fill="both",expand=True)

            hrow=tk.Frame(inner,bg=CARD); hrow.pack(fill="x",pady=(0,6))
            tk.Frame(hrow,bg=BLUE,width=3,height=15).pack(side="left",padx=(0,8))
            tk.Label(hrow,text=f"Variabel: {title}",font=SANSB,
                     bg=CARD,fg=T1).pack(side="left")
            lg=tk.Frame(inner,bg=CARD); lg.pack(fill="x",pady=(0,4))
            for name,fn,a,b,c,col_c in mfs:
                tk.Frame(lg,bg=col_c,width=10,height=10).pack(side="left",padx=(0,3))
                tk.Label(lg,text=name,font=SANSS,bg=CARD,fg=T2).pack(side="left",padx=(0,12))

            cv=tk.Canvas(inner,bg=CANVAS,highlightthickness=1,highlightbackground=BORDER)
            cv.pack(fill="both",expand=True)

            def make_draw(cv,lo,hi,mfs_local,var_key):
                def draw(e=None):
                    cv.update_idletasks()
                    W=cv.winfo_width(); H=cv.winfo_height()
                    if W<10 or H<10: return
                    cv.delete("all")
                    PL,PR,PT,PB=44,14,14,22; N=400
                    def px(x): return PL+(x-lo)/(hi-lo)*(W-PL-PR)
                    def py(mu): return PT+(1-mu)*(H-PT-PB)
                    for mu in [0,.25,.5,.75,1]:
                        y=py(mu)
                        cv.create_line(PL,y,W-PR,y,fill="#E2EBF5",width=1)
                        cv.create_text(PL-4,y,text=f"{mu:.2f}",anchor="e",
                                       font=("Helvetica",7),fill=T3)
                    steps=5
                    for i in range(steps+1):
                        xv=lo+(hi-lo)*i/steps
                        xp=px(xv)
                        cv.create_line(xp,PT,xp,H-PB,fill="#E2EBF5",width=1)
                        cv.create_text(xp,H-PB+4,text=f"{xv:.0f}",anchor="n",
                                       font=("Helvetica",7),fill=T3)
                    cv.create_line(PL,PT,PL,H-PB,fill=BORDER,width=1)
                    cv.create_line(PL,H-PB,W-PR,H-PB,fill=BORDER,width=1)
                    cv.create_text(9,PT+(H-PT-PB)//2,text="μ",
                                   font=("Helvetica",8,"bold"),fill=T3,angle=90)
                    fills=[FR,FS,FT]
                    for fi,(name,fn,a,b,c,col_c) in enumerate(mfs_local):
                        pts=[]
                        for k in range(N+1):
                            xv=lo+(hi-lo)*k/N
                            mu=fn(xv,a,b) if c is None else fn(xv,a,b,c)
                            pts+=[px(xv),py(mu)]
                        fill=fills[fi] if fi<len(fills) else "#EEF"
                        cv.create_polygon([px(lo),py(0)]+pts+[px(hi),py(0)],
                                          fill=fill,outline="")
                        cv.create_line(pts,fill=col_c,width=2)
                    val=None
                    try:
                        if var_key=="umur":    val=round(self.v_umur.get())
                        elif var_key=="bmi":   val=round(self.v_bmi.get(),1)
                        elif var_key=="gula":  val=round(self.v_gula.get())
                        elif var_key=="aktiv": val=round(self.v_aktiv.get())
                    except: pass
                    if val is not None and lo<=val<=hi:
                        xp=px(val)
                        cv.create_line(xp,PT,xp,H-PB,fill=BLUE,width=2,dash=(5,3))
                        cv.create_text(xp,PT+8,text=f"x={val}",
                                       font=("Helvetica",7,"bold"),fill=BLUE,anchor="w")
                return draw

            draw_fn=make_draw(cv,lo,hi,mfs,var_key)
            cv.bind("<Configure>",draw_fn)
            self.mf_canvases.append((cv,draw_fn))

    def _refresh_mf_tab(self):
        for cv,fn in self.mf_canvases:
            fn()

    def _build_manual_tab(self, parent):
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(0,weight=1)

        outer=tk.Frame(parent,bg=BG); outer.grid(row=0,column=0,sticky="nsew",padx=8,pady=8)
        outer.rowconfigure(0,weight=1); outer.columnconfigure(0,weight=1)

        cv=tk.Canvas(outer,bg=BG,highlightthickness=0)
        sb=tk.Scrollbar(outer,orient="vertical",command=cv.yview,
                        troughcolor="#EEF2F7",relief="flat",width=10)
        cv.configure(yscrollcommand=sb.set)
        sb.grid(row=0,column=1,sticky="ns")
        cv.grid(row=0,column=0,sticky="nsew")

        self.manual_inner=tk.Frame(cv,bg=BG)
        self.manual_win=cv.create_window((0,0),window=self.manual_inner,anchor="nw")

        def on_conf(e):
            cv.configure(scrollregion=cv.bbox("all"))
            cv.itemconfig(self.manual_win,width=cv.winfo_width())
        self.manual_inner.bind("<Configure>",on_conf)
        cv.bind("<Configure>",lambda e:(cv.itemconfig(self.manual_win,width=cv.winfo_width()),
                                        cv.configure(scrollregion=cv.bbox("all"))))


        def _on_mousewheel(e):
            cv.yview_scroll(int(-1*(e.delta/120)),"units")
        def _bind_wheel(e):
            cv.bind_all("<MouseWheel>",_on_mousewheel)
        def _unbind_wheel(e):
            cv.unbind_all("<MouseWheel>")
        cv.bind("<Enter>",_bind_wheel)
        cv.bind("<Leave>",_unbind_wheel)

        self.manual_canvas_widget=cv
        self._build_manual_content()

    def _build_manual_content(self):
        p=self.manual_inner
        for w in p.winfo_children(): w.destroy()

        h=getattr(self,"_last_h",None)
        if h is None:
            tk.Label(p,text="Tekan 'Hitung Risiko Diabetes' terlebih dahulu.",
                     font=SANS,bg=BG,fg=T2).pack(padx=16,pady=20)
            return

        umur=round(self.v_umur.get()); bmi=round(self.v_bmi.get(),1)
        gula=round(self.v_gula.get()); aktiv=round(self.v_aktiv.get())
        aR=h["aR"]; aS=h["aS"]; aT=h["aT"]
        crisp=h["crisp"]; label=h["label"]

        col_label={"TINGGI":CT,"SEDANG":CS,"RENDAH":CR}.get(label,T2)

        def section(title, color=BLUE):
            fr=tk.Frame(p,bg=BG); fr.pack(fill="x",padx=12,pady=(12,0))
            tk.Frame(fr,bg=color,width=4,height=18).pack(side="left",padx=(0,10))
            tk.Label(fr,text=title,font=("Helvetica",11,"bold"),
                     bg=BG,fg=T1).pack(side="left",anchor="w")
            tk.Frame(p,bg=BORDER,height=1).pack(fill="x",padx=12,pady=(4,6))

        hdr=self._card(p); hdr.pack(fill="x",padx=12,pady=(8,0))
        hi2=tk.Frame(hdr,bg=CARD,padx=16,pady=12); hi2.pack(fill="x")
        tk.Label(hi2,text="LAPORAN PERHITUNGAN MANUAL",
                 font=("Helvetica",12,"bold"),bg=CARD,fg=T1).pack(anchor="w")
        tk.Label(hi2,text="Metode Fuzzy Mamdani  ·  Defuzzifikasi Centroid (COA)",
                 font=SANSS,bg=CARD,fg=T2).pack(anchor="w")
        self._sep(hi2,4)
        row_in=tk.Frame(hi2,bg=CARD); row_in.pack(fill="x")
        for lbl,val in [("Umur",f"{umur} tahun"),("BMI",f"{bmi} kg/m²"),
                         ("Gula Darah",f"{gula} mg/dL"),("Aktivitas Fisik",f"{aktiv} / 100")]:
            b=tk.Frame(row_in,bg="#F1F4F9",highlightthickness=1,highlightbackground=BORDER)
            b.pack(side="left",padx=(0,8))
            tk.Label(b,text=lbl,font=SANSS,bg="#F1F4F9",fg=T2,padx=10,pady=4).pack()
            tk.Label(b,text=val,font=SANSB,bg="#F1F4F9",fg=T1,padx=10,pady=4).pack()

        section("LANGKAH 1 — Fuzzifikasi")

        fuzz_sections=[
            ("Variabel Umur",f"x = {umur} tahun",[
                ("Muda",   "zmf(x, a=25, b=40)",  h["fz_u"]["Muda"],   CR),
                ("ParuhBaya","trimf(x, a=30, b=45, c=60)",h["fz_u"]["ParuhBaya"],CS),
                ("Tua",    "smf(x, a=50, b=65)",  h["fz_u"]["Tua"],    CT),
            ]),
            ("Variabel BMI",f"x = {bmi} kg/m²",[
                ("Normal",    "zmf(x, a=18, b=25)",       h["fz_b"]["Normal"],    CR),
                ("Overweight","trimf(x, a=22, b=27, c=32)",h["fz_b"]["Overweight"],CS),
                ("Obesitas",  "smf(x, a=27, b=37)",       h["fz_b"]["Obesitas"],  CT),
            ]),
            ("Variabel Gula Darah",f"x = {gula} mg/dL",[
                ("Normal",     "zmf(x, a=90, b=130)",         h["fz_g"]["Normal"],      CR),
                ("Prediabetes","trimf(x, a=100, b=150, c=200)",h["fz_g"]["Prediabetes"],CS),
                ("Diabetes",   "smf(x, a=160, b=220)",        h["fz_g"]["Diabetes"],    CT),
            ]),
            ("Variabel Aktivitas Fisik",f"x = {aktiv} / 100",[
                ("Rendah","zmf(x, a=15, b=40)",        h["fz_a"]["Rendah"],CT),
                ("Sedang","trimf(x, a=25, b=52, c=75)",h["fz_a"]["Sedang"],CS),
                ("Tinggi","smf(x, a=60, b=80)",        h["fz_a"]["Tinggi"],CR),
            ]),
        ]

        for var_title,var_val,sets in fuzz_sections:
            grp=self._card(p); grp.pack(fill="x",padx=12,pady=(0,6))
            gi=tk.Frame(grp,bg=CARD,padx=16,pady=10); gi.pack(fill="x")
            tk.Label(gi,text=f"  {var_title}   ({var_val})",
                     font=SANSB,bg=CARD,fg=T1).pack(anchor="w",pady=(0,6))
            for set_name,formula,val,col_c in sets:
                rw=tk.Frame(gi,bg=CARD); rw.pack(fill="x",pady=2)
                active=val>0.001
                tk.Frame(rw,bg=col_c if active else "#DDE3EC",
                         width=4,height=14).pack(side="left",padx=(0,10))
                tk.Label(rw,text=f"μ_{set_name:<12}",font=("Courier New",9),
                         bg=CARD,fg=T1 if active else T3).pack(side="left")
                tk.Label(rw,text=f"= {formula}",font=("Courier New",9),
                         bg=CARD,fg=T2).pack(side="left",padx=4)
                result_col=col_c if active else T3
                tk.Label(rw,text=f"= {val:.4f}",
                         font=("Courier New",9,"bold"),
                         bg=CARD,fg=result_col).pack(side="left")
                if active:
                    tk.Label(rw,text=" ← AKTIF",font=("Helvetica",7,"bold"),
                             bg=CARD,fg=col_c).pack(side="left")

        section("LANGKAH 2 — Inferensi Mamdani (Firing Strength tiap Rule)")

        grp2=self._card(p); grp2.pack(fill="x",padx=12,pady=(0,6))
        gi2=tk.Frame(grp2,bg=CARD,padx=16,pady=10); gi2.pack(fill="x")

        tk.Label(gi2,text="Operator AND = MIN  |  Hasil = α (firing strength)",
                 font=SANSS,bg=CARD,fg=T2).pack(anchor="w",pady=(0,8))

        for i,(alpha,out,desc) in enumerate(h["all_rules"]):
            active=alpha>0.001
            row=tk.Frame(gi2,bg="#F8FAFB" if i%2==0 else CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER if active else "#EEF2F7")
            row.pack(fill="x",pady=1)
            ri3=tk.Frame(row,bg=row["bg"],padx=10,pady=5); ri3.pack(fill="x")

            out_col={"Tinggi":CT,"Sedang":CS,"Rendah":CR}.get(out,T2)
            tk.Label(ri3,text=f"R{i+1:02d}",font=("Courier New",9,"bold"),
                     bg=row["bg"],fg=BLUE if active else T3,
                     width=4,anchor="w").pack(side="left")
            tk.Label(ri3,text=desc,font=("Courier New",8),
                     bg=row["bg"],fg=T1 if active else T3).pack(side="left",padx=(0,10))
            tk.Label(ri3,text=f"α = {alpha:.4f}",
                     font=("Courier New",9,"bold"),
                     bg=row["bg"],
                     fg=out_col if active else T3).pack(side="right")
            if active:
                tk.Label(ri3,text=f"[{out}]",font=("Helvetica",8,"bold"),
                         bg=row["bg"],fg=out_col).pack(side="right",padx=(0,8))

        ag=tk.Frame(gi2,bg=CARD); ag.pack(fill="x",pady=(10,0))
        self._sep(ag,3)
        tk.Label(ag,text="Agregasi (MAX per kategori output):",
                 font=SANSB,bg=CARD,fg=T1).pack(anchor="w",pady=(4,4))
        for name,val,col_c in [("Rendah",aR,CR),("Sedang",aS,CS),("Tinggi",aT,CT)]:
            rw=tk.Frame(ag,bg=CARD); rw.pack(fill="x",pady=2)
            tk.Label(rw,text=f"  α_{name:<8} = MAX(semua rule {name})",
                     font=("Courier New",9),bg=CARD,fg=T2).pack(side="left")
            tk.Label(rw,text=f"= {val:.4f}",
                     font=("Courier New",9,"bold"),bg=CARD,
                     fg=col_c if val>0.001 else T3).pack(side="left",padx=6)

        section("LANGKAH 3 — Defuzzifikasi (Metode Centroid / Center of Area)")

        df=self._card(p); df.pack(fill="x",padx=12,pady=(0,6))
        di=tk.Frame(df,bg=CARD,padx=16,pady=12); di.pack(fill="x")

        formula_box=tk.Frame(di,bg="#F1F4F9",highlightthickness=1,
                             highlightbackground=BORDER)
        formula_box.pack(fill="x",pady=(0,10))
        fi2=tk.Frame(formula_box,bg="#F1F4F9",padx=14,pady=10); fi2.pack(fill="x")
        tk.Label(fi2,text="Rumus:",font=SANSS,bg="#F1F4F9",fg=T2).pack(anchor="w")
        tk.Label(fi2,text="z* = Σ [ x · μ(x) ] / Σ [ μ(x) ]",
                 font=("Courier New",11,"bold"),bg="#F1F4F9",fg=BLUE).pack(anchor="w")
        tk.Label(fi2,text="     dengan μ(x) = max dari semua MF output yang ter-clip",
                 font=("Courier New",8),bg="#F1F4F9",fg=T2).pack(anchor="w")

        mf_note=tk.Frame(di,bg=CARD); mf_note.pack(fill="x",pady=(0,8))
        tk.Label(mf_note,text="MF Output yang digunakan:",font=SANSB,
                 bg=CARD,fg=T1).pack(anchor="w",pady=(0,4))
        for name,val,col_c,fn_name in [
            ("Rendah",aR,CR,"trimf(x, 0, 20, 40)"),
            ("Sedang",aS,CS,"trimf(x, 30, 50, 70)"),
            ("Tinggi",aT,CT,"trimf(x, 60, 80, 100)"),
        ]:
            rw=tk.Frame(mf_note,bg=CARD); rw.pack(fill="x",pady=1)
            active=val>0.001
            tk.Frame(rw,bg=col_c if active else "#DDE3EC",
                     width=4,height=14).pack(side="left",padx=(0,8))
            tk.Label(rw,text=f"MF_{name:<8}",font=("Courier New",9),
                     bg=CARD,fg=T1 if active else T3).pack(side="left")
            tk.Label(rw,text=f"= {fn_name}",font=("Courier New",9),
                     bg=CARD,fg=T2).pack(side="left",padx=4)
            tk.Label(rw,text=f"di-clip pada α = {val:.4f}",
                     font=("Courier New",9,"bold"),bg=CARD,
                     fg=col_c if active else T3).pack(side="left",padx=8)

        self._sep(di,6)

        tk.Label(di,text="Sampel perhitungan numerik (interval Δx = 0.5):",
                 font=SANSS,bg=CARD,fg=T2).pack(anchor="w",pady=(0,6))

        tbl_frame=tk.Frame(di,bg=CARD); tbl_frame.pack(fill="x")
        hdrs=["x","μ_Rendah(x)","μ_Sedang(x)","μ_Tinggi(x)","μ_agg(x)","x · μ_agg(x)"]
        col_widths=[6,13,13,13,12,14]
        hdr_row=tk.Frame(tbl_frame,bg="#F1F4F9"); hdr_row.pack(fill="x")
        for hh,ww in zip(hdrs,col_widths):
            tk.Label(hdr_row,text=hh,font=("Courier New",8,"bold"),
                     bg="#F1F4F9",fg=BLUE,width=ww,anchor="e",
                     padx=4,pady=3,relief="flat").pack(side="left")

        sample_xs=[0,10,20,25,30,40,50,60,70,80,90,100]
        for i,x in enumerate(sample_xs):
            mu_r=min(aR,mf_R(x)); mu_s=min(aS,mf_S(x)); mu_t=min(aT,mf_T(x))
            mu_agg=max(mu_r,mu_s,mu_t); contrib=x*mu_agg
            row_bg=CARD if i%2==0 else "#F7FAFD"
            rw=tk.Frame(tbl_frame,bg=row_bg); rw.pack(fill="x")
            for val,ww in zip([f"{x:.1f}",f"{mu_r:.4f}",f"{mu_s:.4f}",
                                f"{mu_t:.4f}",f"{mu_agg:.4f}",f"{contrib:.4f}"],
                               col_widths):
                is_agg=col_widths.index(ww)==4
                is_contrib=col_widths.index(ww)==5
                fg=BLUE if (is_agg and mu_agg>0.001) else (CS if is_contrib and contrib>0 else T1)
                tk.Label(rw,text=val,font=("Courier New",8),
                         bg=row_bg,fg=fg,width=ww,anchor="e",
                         padx=4,pady=2).pack(side="left")

        note_row=tk.Frame(tbl_frame,bg="#F1F4F9"); note_row.pack(fill="x")
        tk.Label(note_row,text="  ... (500 titik dihitung, hanya 12 sampel ditampilkan)",
                 font=("Helvetica",7),bg="#F1F4F9",fg=T3,pady=3).pack(anchor="w")

        self._sep(di,8)

        res_box=tk.Frame(di,bg="#F1F4F9",highlightthickness=2,
                         highlightbackground=col_label)
        res_box.pack(fill="x")
        rb=tk.Frame(res_box,bg="#F1F4F9",padx=14,pady=12); rb.pack(fill="x")
        tk.Label(rb,text="HASIL AKHIR",font=("Helvetica",8,"bold"),
                 bg="#F1F4F9",fg=T3).pack(anchor="w")
        tk.Label(rb,
                 text=f"Σ [ x · μ(x) ]  =  {h['num']:.4f}",
                 font=("Courier New",10),bg="#F1F4F9",fg=T1).pack(anchor="w")
        tk.Label(rb,
                 text=f"Σ [ μ(x) ]       =  {h['den']:.4f}",
                 font=("Courier New",10),bg="#F1F4F9",fg=T1).pack(anchor="w")
        self._sep(rb,4)
        tk.Label(rb,
                 text=f"z*  =  {h['num']:.4f}  /  {h['den']:.4f}  =  {crisp:.4f}",
                 font=("Courier New",11,"bold"),bg="#F1F4F9",fg=BLUE).pack(anchor="w")
        self._sep(rb,4)
        conc=tk.Frame(rb,bg="#F1F4F9"); conc.pack(fill="x")
        tk.Label(conc,text="Kesimpulan:  Nilai crisp = ",
                 font=("Helvetica",10),bg="#F1F4F9",fg=T1).pack(side="left")
        tk.Label(conc,text=f"{crisp:.2f}",
                 font=("Helvetica",11,"bold"),bg="#F1F4F9",fg=col_label).pack(side="left")
        tk.Label(conc,text="  →  Risiko Diabetes: ",
                 font=("Helvetica",10),bg="#F1F4F9",fg=T1).pack(side="left")
        tk.Label(conc,text=label,
                 font=("Helvetica",13,"bold"),bg="#F1F4F9",fg=col_label).pack(side="left")

        th=tk.Frame(rb,bg="#F1F4F9"); th.pack(fill="x",pady=(6,0))
        tk.Label(th,text="Threshold: z* < 35 → RENDAH  |  35 ≤ z* < 60 → SEDANG  |  z* ≥ 60 → TINGGI",
                 font=("Helvetica",8),bg="#F1F4F9",fg=T2).pack(anchor="w")

    def _interpretasi(self):
        outer=tk.Frame(self,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        outer.grid(row=2,column=0,sticky="ew",padx=12,pady=(0,10))

        wrap=tk.Frame(outer,bg=CARD,padx=14,pady=10); wrap.pack(fill="x")
        hrow=tk.Frame(wrap,bg=CARD); hrow.pack(fill="x",pady=(0,6))
        tk.Frame(hrow,bg=BLUE,width=3,height=15).pack(side="left",padx=(0,8))
        tk.Label(hrow,text="Interpretasi Klinis",font=SANSB,bg=CARD,fg=T1).pack(side="left")
        tk.Label(hrow,text="  —  kotak yang sesuai hasil akan disorot secara otomatis",
                 font=SANSS,bg=CARD,fg=T3).pack(side="left",pady=(2,0))
        self._sep(wrap,4)

        boxes=tk.Frame(wrap,bg=CARD); boxes.pack(fill="x")
        boxes.columnconfigure(0,weight=1); boxes.columnconfigure(1,weight=1)
        boxes.columnconfigure(2,weight=1)

        DATA=[
            ("RENDAH",CR,FR,FR2,
             "Risiko diabetes RENDAH.",
             "Profil pasien menunjukkan risiko minimal. Pertahankan pola hidup sehat, "
             "konsumsi makanan bergizi, dan tetap aktif berolahraga. "
             "Lakukan skrining ulang setiap 1–2 tahun."),
            ("SEDANG",CS,FS,FS2,
             "Risiko diabetes SEDANG.",
             "Terdapat sejumlah faktor risiko. Disarankan perbaikan pola makan, "
             "peningkatan aktivitas fisik, dan konsultasi dokter dalam waktu dekat."),
            ("TINGGI",CT,FT,FT2,
             "Risiko diabetes TINGGI.",
             "Risiko signifikan terdeteksi. Segera lakukan pemeriksaan HbA1c & "
             "gula darah puasa, dan konsultasi dokter untuk penanganan lebih lanjut."),
        ]

        self.iboxes={}
        for ci,(lvl,fg,bg_n,bg_a,title,body) in enumerate(DATA):
            box=tk.Frame(boxes,bg=bg_n,highlightthickness=2,highlightbackground=bg_n)
            box.grid(row=0,column=ci,sticky="nsew",padx=(0 if ci==0 else 8,0))
            inn=tk.Frame(box,bg=bg_n,padx=12,pady=10); inn.pack(fill="both",expand=True)
            brow=tk.Frame(inn,bg=bg_n); brow.pack(fill="x",pady=(0,5))
            badge=tk.Label(brow,text=f"  {lvl}  ",font=SANSB,
                           bg=fg,fg="white",padx=4,pady=2); badge.pack(side="left")
            tlbl=tk.Label(inn,text=title,font=SANSB,bg=bg_n,fg=T1,anchor="w")
            tlbl.pack(fill="x")
            blbl=tk.Label(inn,text=body,font=SANSS,bg=bg_n,fg=T2,
                          wraplength=360,justify="left",anchor="nw")
            blbl.pack(fill="x",pady=(3,0))
            self.iboxes[lvl]=dict(box=box,inn=inn,badge=badge,tlbl=tlbl,blbl=blbl,
                                   fg=fg,bg_n=bg_n,bg_a=bg_a)

    def _slider(self,parent,label,var,lo,hi,fmt,step=1):
        f=tk.Frame(parent,bg=CARD); f.pack(fill="x",pady=3)
        top=tk.Frame(f,bg=CARD); top.pack(fill="x")
        tk.Label(top,text=label,font=SANS,bg=CARD,fg=T2,anchor="w").pack(side="left")
        vl=tk.Label(top,text="",font=SANSB,bg=CARD,fg=BLUE,anchor="e"); vl.pack(side="right")
        TH=6; TR=9; CH=TR*2+6
        cv=tk.Canvas(f,bg=CARD,height=CH,highlightthickness=0,cursor="hand2")
        cv.pack(fill="x",pady=(1,0))
        st={"d":False}
        def v2x(v,W): return TR+2+(v-lo)/max(hi-lo,1)*max(W-2*(TR+2),1)
        def x2v(x,W): return max(lo,min(hi,lo+(x-TR-2)/max(W-2*(TR+2),1)*(hi-lo)))
        def draw(v=None):
            if v is None: v=var.get()
            W=cv.winfo_width()
            if W<10: return
            cv.delete("all"); p2=TR+2; cy=CH//2
            cv.create_rectangle(p2,cy-TH//2,W-p2,cy+TH//2,fill="#DDE8F4",outline="")
            tx=v2x(v,W)
            if tx>p2+1:
                cv.create_rectangle(p2,cy-TH//2,tx,cy+TH//2,fill=BLUE_L,outline="")
            cv.create_oval(tx-TR,cy-TR,tx+TR,cy+TR,fill=BLUE,outline="white",width=2)

        def sset(x):
            W=cv.winfo_width(); v=x2v(x,W)
            if step: v=round(v/step)*step
            var.set(v); vl.config(text=fmt(var.get())); draw(var.get())
            if getattr(self,"_hitung_job",None):
                self.after_cancel(self._hitung_job)
            self._hitung_job=self.after(30,self._hitung)
        cv.bind("<ButtonPress-1>",  lambda e:(st.update(d=True),sset(e.x)))
        cv.bind("<B1-Motion>",      lambda e:st["d"] and sset(e.x))
        cv.bind("<ButtonRelease-1>",lambda e:st.update(d=False))
        cv.bind("<Configure>",      lambda e:draw())
        var.trace_add("write",lambda *_:(vl.config(text=fmt(var.get())),draw()))

    def _draw_gauge(self,crisp,label):
        c=self.gauge; c.delete("all")
        W=c.winfo_width()
        if W<10: return
        H=22; pad=3
        c.create_rectangle(0,pad,W,H-pad,fill="#E4EBF5",outline="")
        col={"RENDAH":CR,"SEDANG":CS,"TINGGI":CT}.get(label,BLUE)
        fw=max(0,int(W*crisp/100))
        if fw>0: c.create_rectangle(0,pad,fw,H-pad,fill=col,outline="")
        tc="white" if fw>W*0.45 else T2
        c.create_text(W//2,H//2,text=f"{crisp:.1f} / 100",
                      font=("Helvetica",8,"bold"),fill=tc)

    def _axes(self,c,W,H,PL,PR,PT,PB):
        for mu in [0,.25,.5,.75,1]:
            py=PT+(1-mu)*(H-PT-PB)
            c.create_line(PL,py,W-PR,py,fill="#E2EBF5",width=1)
            c.create_text(PL-4,py,text=f"{mu:.2f}",anchor="e",
                          font=("Helvetica",7),fill=T3)
        for xt in range(0,101,25):
            px=PL+(xt/100)*(W-PL-PR)
            c.create_line(px,PT,px,H-PB,fill="#E2EBF5",width=1)
            c.create_text(px,H-PB+4,text=str(xt),anchor="n",
                          font=("Helvetica",7),fill=T3)
        c.create_line(PL,PT,PL,H-PB,fill=BORDER,width=1)
        c.create_line(PL,H-PB,W-PR,H-PB,fill=BORDER,width=1)
        c.create_text(9,PT+(H-PT-PB)//2,text="μ",
                      font=("Helvetica",8,"bold"),fill=T3,angle=90)
        c.create_text(W//2,H-5,text="Risiko Diabetes (0 – 100)",
                      font=("Helvetica",7),fill=T3)

    def _draw_graph(self,aR,aS,aT,crisp):
        for cv in (self.cmf,self.cagg): cv.update_idletasks()
        W1=self.cmf.winfo_width(); H1=self.cmf.winfo_height()
        W2=self.cagg.winfo_width(); H2=self.cagg.winfo_height()
        if W1<10 or H1<10: return
        PL,PR,PT,PB=36,14,14,22; N=400
        def px(x,W): return PL+(x/100)*(W-PL-PR)
        def py(mu,H): return PT+(1-mu)*(H-PT-PB)
        cfgs=[("Rendah",mf_R,aR,CR,FR),("Sedang",mf_S,aS,CS,FS),("Tinggi",mf_T,aT,CT,FT)]
        c=self.cmf; c.delete("all"); self._axes(c,W1,H1,PL,PR,PT,PB)
        for _,fn,_,col,fill in cfgs:
            pts=[]
            for k in range(N+1): x=k/N*100; pts+=[px(x,W1),py(fn(x),H1)]
            c.create_polygon([px(0,W1),py(0,H1)]+pts+[px(100,W1),py(0,H1)],fill=fill,outline="")
            c.create_line(pts,fill=col,width=2)
        c2=self.cagg; c2.delete("all"); self._axes(c2,W2,H2,PL,PR,PT,PB)
        for _,fn,alpha,col,fill in cfgs:
            if alpha<0.001: continue
            pts=[]
            for k in range(N+1): x=k/N*100; pts+=[px(x,W2),py(min(alpha,fn(x)),H2)]
            c2.create_polygon([px(0,W2),py(0,H2)]+pts+[px(100,W2),py(0,H2)],fill=fill,outline="")
        for _,fn,_,col,_ in cfgs:
            pts=[]
            for k in range(N+1): x=k/N*100; pts+=[px(x,W2),py(fn(x),H2)]
            c2.create_line(pts,fill=col,width=1,dash=(4,4))
        for _,fn,alpha,col,_ in cfgs:
            if alpha<0.001: continue
            xs=[k/N*100 for k in range(N+1) if fn(k/N*100)>0.001]
            if xs:
                ya=py(alpha,H2)
                c2.create_line(px(xs[0],W2),ya,px(xs[-1],W2),ya,fill=col,width=1,dash=(2,3))
                c2.create_text(px(xs[-1],W2)+3,ya,text=f"α={alpha:.2f}",
                               anchor="w",font=("Helvetica",7),fill=col)
        agg=[]
        for k in range(N+1):
            x=k/N*100
            mu=max(min(aR,mf_R(x)),min(aS,mf_S(x)),min(aT,mf_T(x)))
            agg+=[px(x,W2),py(mu,H2)]
        if len(agg)>=4: c2.create_line(agg,fill=T2,width=1.5)
        if crisp>0:
            pxc=px(crisp,W2)
            c2.create_line(pxc,PT,pxc,H2-PB,fill=BLUE,width=2,dash=(6,3))
            anch="w" if pxc<W2*0.72 else "e"
            tx=pxc+5 if anch=="w" else pxc-5
            c2.create_text(tx,PT+9,text=f"z* = {crisp:.1f}",
                           anchor=anch,font=("Helvetica",8,"bold"),fill=BLUE)
            c2.create_oval(pxc-5,H2-PB-5,pxc+5,H2-PB+5,fill=BLUE,outline="white",width=2)

    def _hitung(self):
        self._hitung_job=None
        umur=round(self.v_umur.get()); bmi=round(self.v_bmi.get(),1)
        gula=round(self.v_gula.get()); aktiv=round(self.v_aktiv.get())
        h=hitung(umur,bmi,gula,aktiv)
        self._last_h=h
        aR,aS,aT=h["aR"],h["aS"],h["aT"]
        crisp=h["crisp"]; label=h["label"]
        self._crisp=crisp; self._label=label
        col={"TINGGI":CT,"SEDANG":CS,"RENDAH":CR}.get(label,T2)

        self.lbl_hasil.config(text=label,fg=col)
        self.lbl_crisp.config(text=f"Nilai crisp:  {crisp:.2f} / 100")
        self._draw_gauge(crisp,label)
        self.gauge.bind("<Configure>",lambda e:self._draw_gauge(crisp,label))

        for name,key in [("Rendah","aR"),("Sedang","aS"),("Tinggi","aT")]:
            alpha=h[key]; tr,fl=self.abars[name]
            tr.update_idletasks()
            fl.place(x=0,y=0,height=10,width=max(int(tr.winfo_width()*alpha),0))
            self.avals[name].config(text=f"{alpha:.3f}")

        self.rtxt.config(state="normal"); self.rtxt.delete("1.0","end")
        if h["rules"]:
            for i,(alpha,out,desc) in enumerate(h["rules"]):

                self.rtxt.insert("end",f"R{i+1:02d} ","num")
                self.rtxt.insert("end",f"α={alpha:.3f}  ","alpha")
                self.rtxt.insert("end",f"[{out}]\n",out.lower())
                self.rtxt.insert("end",f"     {desc}\n\n","desc")
        else:
            self.rtxt.insert("end","Tidak ada rule yang aktif.","num")
        self.rtxt.config(state="disabled")

        # Hapus widget lama terlebih dahulu
        for w in self.fuzz_frame.winfo_children():
            w.destroy()

        def _rebuild_fuzz():
            # Pastikan frame sudah punya parent yang ter-render
            # dengan memanggil update() (bukan hanya update_idletasks)
            # untuk flush semua pending geometry event
            try:
                self.fuzz_frame.update()
            except Exception:
                pass

            for vname,mfs,lbls in [
                ("Umur",    h["fz_u"],[("Muda",CR),("ParuhBaya",CS),("Tua",CT)]),
                ("BMI",     h["fz_b"],[("Normal",CR),("Overweight",CS),("Obesitas",CT)]),
                ("Gula",    h["fz_g"],[("Normal",CR),("Prediabetes",CS),("Diabetes",CT)]),
                ("Aktivitas",h["fz_a"],[("Rendah",CT),("Sedang",CS),("Tinggi",CR)]),
            ]:
                rw=tk.Frame(self.fuzz_frame,bg=CARD); rw.pack(fill="x",pady=2)
                tk.Label(rw,text=vname,font=("Helvetica",8,"bold"),
                         bg=CARD,fg=T2,width=9,anchor="w").pack(side="left")
                for lname,lcol in lbls:
                    v=mfs.get(lname,0); on=v>0.001
                    tk.Label(rw,text=f"{lname[:5]}:{v:.2f}",
                             font=("Helvetica",7,"bold" if on else "normal"),
                             bg=lcol if on else "#E8EEF5",
                             fg="white" if on else T3,
                             padx=3,pady=2).pack(side="left",padx=1)

        _rebuild_fuzz()
        self.after(50, _rebuild_fuzz)

        for lvl,info in self.iboxes.items():
            on=(lvl==label)
            bg=info["bg_a"] if on else info["bg_n"]
            info["box"].config(highlightbackground=info["fg"] if on else info["bg_n"])
            info["inn"].config(bg=bg)
            info["badge"].config(bg=info["fg"] if on else "#BBBBBB",fg="white")
            info["tlbl"].config(bg=bg,font=SANSB,fg=T1 if on else T3)
            info["blbl"].config(bg=bg,fg=T1 if on else T3)

        self._draw_graph(aR,aS,aT,crisp)
        self.after(60,lambda:self._draw_graph(aR,aS,aT,crisp))
        self._refresh_mf_tab()

        if self._is_manual_tab_active():
            self._build_manual_content()


if __name__=="__main__":
    App().mainloop()
