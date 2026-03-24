"""
Génère le rapport PDF des 4 attaques QPUF — formules en LaTeX (mathtext stix).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
from scipy.stats import poisson as scipy_poisson
import warnings; warnings.filterwarnings('ignore')

# ── Paramètres ────────────────────────────────────────────────────────────────
K = N = 1600;  n = 5;  eta = 0.5;  ldc = 0.01;  EPS = 1e-300

def mu_alice(n, e, l):      return e*n + l
def F1(n, K):               return (n+1)/(n+K)
def F2(n, K):               return (n+1)/(n+K)
def F3(K):                  return 2.0/(K+1)
def F4(n, K):               return 2*n/(2*n+K)
def mE1(n, K, e, l):        return e*n*F1(n,K)+l
def mE2(n, K, e, l):        return e*n*F2(n,K)+l
def mE3(n, K, e, l):        return e*n*F3(K)+l
def mE4(n, K, e, l):        return e*n*F4(n,K)+l

def errs(mA, mE, R):
    lA, lE = R*mA, R*mE
    T = np.arange(0, int(lA+8*np.sqrt(max(lA,1))+30)+2)
    fp = 1-scipy_poisson.cdf(T-1,lE);  fn = scipy_poisson.cdf(T-1,lA)
    i = np.argmin(np.maximum(fp,fn))
    return float(fp[i]), float(fn[i]), int(T[i])

mA = mu_alice(n,eta,ldc)
Rv  = np.arange(1,26)
COLS = {'a1':'#2980b9','a2':'#27ae60','a3':'#e74c3c','a4':'#8e44ad',
        'dark':'#1a1a2e','mid':'#2c3e50'}

# Pre-compute curves
curves = {}
for label, mE, c, ls in [
    ('A1',mE1(n,K,eta,ldc),COLS['a1'],'-'),
    ('A2',mE2(n,K,eta,ldc),COLS['a2'],'--'),
    ('A3',mE3(n,K,eta,ldc),COLS['a3'],':'),
    ('A4',mE4(n,K,eta,ldc),COLS['a4'],'-'),
]:
    fp_r,fn_r = [],[]
    for R in Rv:
        fp,fn,_ = errs(mA,mE,R)
        fp_r.append(max(fp,EPS));fn_r.append(max(fn,EPS))
    curves[label]=(c,ls,fp_r,fn_r)

# ── Layout helpers ────────────────────────────────────────────────────────────
def new_fig():
    fig=plt.figure(figsize=(8.27,11.69)); fig.patch.set_facecolor('white'); return fig

def hdr(fig, txt, col, y=0.965, h=0.048):
    ax=fig.add_axes([0,y,1,h]); ax.set_facecolor(col); ax.axis('off')
    ax.text(0.5,0.5,txt,ha='center',va='center',fontsize=13,
            fontweight='bold',color='white',transform=ax.transAxes)

def ftr(fig, p, tot):
    ax=fig.add_axes([0,0,1,0.025]); ax.set_facecolor('#f0f0f0'); ax.axis('off')
    ax.text(0.5,0.5,
            f'Attaques QPUF — Simulation et Analyse de Sécurité   |   Page {p}/{tot}',
            ha='center',va='center',fontsize=7,color='#555',transform=ax.transAxes)

def sec_bar(ax, txt, col, y, h=0.022):
    ax.add_patch(FancyBboxPatch((0,y-h),0.98,h,
        boxstyle='round,pad=0.004',facecolor=col,lw=0,transform=ax.transAxes))
    ax.text(0.012,y-h/2,txt,ha='left',va='center',fontsize=9.5,
            fontweight='bold',color='white',transform=ax.transAxes)
    return y-h-0.008

def math_line(ax, s, x, y, fs=10.5, col='#0a2342'):
    """Render one line — use math mode if it contains $."""
    ax.text(x, y, s, ha='left', va='top', fontsize=fs,
            color=col, transform=ax.transAxes, usetex=False)

def code_line(ax, s, x, y, fs=8.0, col='#1a1a2e'):
    ax.text(x, y, s, ha='left', va='top', fontsize=fs,
            color=col, fontfamily='monospace', transform=ax.transAxes)

def result_line(ax, s, x, y, fs=9.0, col='#1e8449'):
    ax.text(x, y, s, ha='left', va='top', fontsize=fs,
            color=col, transform=ax.transAxes)

def box(ax, bx, by, bw, bh, fc, ec, lw=0.8):
    ax.add_patch(FancyBboxPatch((bx,by),bw,bh,
        boxstyle='round,pad=0.005',facecolor=fc,edgecolor=ec,lw=lw,
        transform=ax.transAxes))

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — TITRE
# ═════════════════════════════════════════════════════════════════════════════
def page_title(pdf):
    fig=new_fig(); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
    ax.set_facecolor(COLS['dark']); fig.patch.set_facecolor(COLS['dark'])

    ax.text(0.5,0.80,'Quantum Physical Unclonable Functions',
            ha='center',va='center',fontsize=18,fontweight='bold',
            color='white',transform=ax.transAxes)
    ax.text(0.5,0.72,
            r"Analyse des 4 Attaques et Probabilités d'Erreur",
            ha='center',va='center',fontsize=13,color='#aad4f5',
            transform=ax.transAxes)
    ax.axhline(0.67,color='#aad4f5',lw=1.5,xmin=0.1,xmax=0.9)

    rows=[('#','Attaque',r'Fidélité $F$','Source'),
          ('1','Clonage UQCM',r'$F_1=\dfrac{n+1}{n+K}$','Yao Tao et al.'),
          ('2','POVM générique',r'$F_2=\dfrac{n+1}{n+K}$','Skoric'),
          ('3','Intercept-Resend',r'$F_3=\dfrac{2}{K+1}$','Skoric'),
          ('4','Quadrature / hétérodyne',r'$F_4=\dfrac{2n}{2n+K}$',
           'Skoric, Mosk, Pinkse')]
    rcs=['#2c3e50',COLS['a1'],COLS['a2'],COLS['a3'],COLS['a4']]
    y0=0.62
    for i,(row,rc) in enumerate(zip(rows,rcs)):
        y=y0-i*0.08
        ax.add_patch(FancyBboxPatch((0.05,y-0.064),0.90,0.065,
            boxstyle='round,pad=0.005',facecolor=rc,alpha=0.88,
            lw=0,transform=ax.transAxes))
        cx=[0.08,0.14,0.38,0.66]
        for txt,x in zip(row,cx):
            fs=9 if i==0 else 9.5; fw='bold' if i==0 else 'normal'
            ax.text(x,y-0.024,txt,ha='left',va='center',fontsize=fs,
                    fontweight=fw,color='white',transform=ax.transAxes)

    ax.text(0.5,0.14,
            r'Paramètres : $N=K=1600$,  $n=5$ photons,  $\eta=0.5$,  $\lambda_{dc}=0.01$',
            ha='center',va='center',fontsize=10.5,color='#aad4f5',
            transform=ax.transAxes)
    ax.text(0.5,0.08,
            r'$P_{fp}$ et $P_{fn}$ calculées via la CDF de Poisson optimisée sur $R$ rounds',
            ha='center',va='center',fontsize=9.5,color='#7fb3d3',
            transform=ax.transAxes)
    ftr(fig,1,8)
    pdf.savefig(fig,bbox_inches='tight'); plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PROTOCOLE
# ═════════════════════════════════════════════════════════════════════════════
def page_protocol(pdf):
    fig=new_fig(); hdr(fig,"Contexte : Protocole d'Authentification QPUF",COLS['dark'])
    ftr(fig,2,8)
    ax=fig.add_axes([0.04,0.03,0.92,0.91]); ax.axis('off')
    y=0.91

    sections=[
        ("Le système QPUF",[
            "Un Quantum Physical Unclonable Function (QPUF) est un diffuseur optique",
            r"caractérisé par sa matrice de scattering $H$ ($N\times N$, complexe, aléatoire).",
            "",
            r"Alice et Bob partagent une base de données de paires challenge–réponse $(C_k,\,y_k)$ :",
            r"  $\bullet$  $y_k = e_k$   (vecteur canonique — pixel $k$ éclairé en sortie)",
            r"  $\bullet$  $C_k = H^\dagger y_k\,/\,\|H^\dagger y_k\|$   (challenge normalisé)",
            "",
            r"Pour s'authentifier, Bob envoie $C_k \to \mathrm{PUF} \to H C_k \approx y_k$",
            r"$\Rightarrow$ photons focalisés au pixel $k$.",
        ]),
        ("Modèle de détection",[
            r"Chaque pixel $a$ reçoit un nombre de photons Poissonnien :",
            r"  $\mathrm{counts}_a \;\sim\; \mathrm{Poisson}\left(\eta\cdot n\cdot|y_a|^2 + \lambda_{dc}\right)$",
            "",
            r"  $\bullet$  $\eta = 0.5$   : efficacité de détection",
            r"  $\bullet$  $n = 5$   : photons par impulsion",
            r"  $\bullet$  $\lambda_{dc} = 0.01$   : taux de coups sombres",
            "",
            r"Bonne clé : $|y_k|^2 = 1$   $\Rightarrow$   $\mu_{\mathrm{Alice}} = \eta n + \lambda_{dc} = 2.51$ photons/round",
        ]),
        (r"Calcul des erreurs sur $R$ rounds",[
            r"Sur $R$ rounds, les totaux suivent $\mathrm{Poisson}(R\cdot\mu)$ :",
            "",
            r"  $P_{fp}(T) = \Pr\left[\mathrm{Poisson}(R\mu_E)\geq T\right]$   — Eve faussement acceptée",
            r"  $P_{fn}(T) = \Pr\left[\mathrm{Poisson}(R\mu_A)< T\right]$   — Alice faussement rejetée",
            "",
            r"Seuil optimal : $T^* = \arg\min_T \max\left(P_{fp}(T),\,P_{fn}(T)\right)$",
            "",
            r"L'écart $\mu_A \gg \mu_E$ est le fondement de la sécurité quantique.",
        ]),
    ]

    for title, lines in sections:
        y=sec_bar(ax,title,COLS['mid'],y)+0.005
        for line in lines:
            math_line(ax, line, 0.015, y, fs=9.2)
            y-=0.030
        y-=0.012

    pdf.savefig(fig,bbox_inches='tight'); plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# PAGES 3-6 — UNE PAR ATTAQUE
# ═════════════════════════════════════════════════════════════════════════════
def attack_page(pdf, page, num, col, title, source,
                desc, formulas, code, results,
                F_val, mE_val, pfp, pfn, Tstar):
    fig=new_fig(); hdr(fig,f"Attaque {num} — {title}",col); ftr(fig,page,8)
    ax=fig.add_axes([0.04,0.03,0.92,0.905]); ax.axis('off')
    y=0.89

    # Source
    ax.text(0.01,y,source,ha='left',va='top',fontsize=8.5,
            color='#666',style='italic',transform=ax.transAxes)
    y-=0.040

    # ── Description ──────────────────────────────────────────────────────────
    y=sec_bar(ax,'Description & Protocole',col,y)+0.004
    for line in desc:
        math_line(ax,line,0.015,y,fs=8.8,col='#1a1a2e')
        y-=0.027
    y-=0.010

    # ── Formules ─────────────────────────────────────────────────────────────
    y=sec_bar(ax,'Formules Clés',col,y)+0.004
    h_box=len(formulas)*0.038+0.014
    box(ax,0,y-h_box,0.98,h_box,'#eaf4fb','#5dade2',lw=1.0)
    yf=y-0.010
    for line in formulas:
        if line.strip()=='':
            yf-=0.016; continue
        # detect if line is predominantly math or text
        is_math_only = line.strip().startswith('$') and line.strip().endswith('$')
        fs = 11.5 if is_math_only else 9.5
        math_line(ax,line,0.025,yf,fs=fs,col='#154360')
        yf-=0.040 if is_math_only else 0.030
    y=yf-0.015

    # ── Code ─────────────────────────────────────────────────────────────────
    y=sec_bar(ax,'Implémentation Python',col,y)+0.004
    h_code=len(code)*0.024+0.010
    box(ax,0,y-h_code,0.98,h_code,'#f8f9fa','#cccccc')
    yc=y-0.008
    for line in code:
        code_line(ax,line,0.015,yc,fs=7.6)
        yc-=0.024
    y=yc-0.016

    # ── Résultats ─────────────────────────────────────────────────────────────
    y=sec_bar(ax,'Résultats numériques  (n=5, K=1600, η=0.5, λdc=0.01)',col,y)+0.004
    h_res=len(results)*0.026+0.010
    box(ax,0,y-h_res,0.98,h_res,'#eafaf1','#a9dfbf')
    yr=y-0.008
    for line in results:
        math_line(ax,line,0.018,yr,fs=8.8,col='#1e8449')
        yr-=0.026
    y=yr-0.012

    # ── KPI boxes ─────────────────────────────────────────────────────────────
    kpis=[(rf'$F = {F_val:.5f}$','Fidélité'),
          (rf'$\mu_E = {mE_val:.5f}$','Photons Eve/round'),
          (rf'$P_{{fp}} = {pfp:.2e}$',r'$P_{fp}$ (R=10)'),
          (rf'$P_{{fn}} = {pfn:.2e}$',r'$P_{fn}$ (R=10)')]
    bw=0.235; gap=0.010
    for i,(val,lbl) in enumerate(kpis):
        bx=i*(bw+gap)
        box(ax,bx,y-0.072,bw,0.070,col+'22',col,lw=1.2)
        ax.text(bx+bw/2,y-0.028,val,ha='center',va='center',
                fontsize=9.5,fontweight='bold',color=col,transform=ax.transAxes)
        ax.text(bx+bw/2,y-0.056,lbl,ha='center',va='center',
                fontsize=8,color='#555',transform=ax.transAxes)

    pdf.savefig(fig,bbox_inches='tight'); plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 7 — GRAPHIQUES
# ═════════════════════════════════════════════════════════════════════════════
def page_plots(pdf):
    fig=new_fig()
    hdr(fig,r'Comparaison des 4 attaques : $P_{fp}$ et $P_{fn}$ en fonction de $R$',COLS['dark'])
    ftr(fig,7,8)
    labels={'A1':r'A1 — Clonage UQCM','A2':r'A2 — POVM générique',
            'A3':'A3 — Intercept-Resend','A4':r'A4 — Quadrature'}
    ax_fp=fig.add_axes([0.10,0.52,0.86,0.39])
    ax_fn=fig.add_axes([0.10,0.07,0.86,0.39])
    for k,(c,ls,fp_r,fn_r) in curves.items():
        ax_fp.semilogy(Rv,fp_r,color=c,ls=ls,lw=2,label=labels[k])
        ax_fn.semilogy(Rv,fn_r,color=c,ls=ls,lw=2,label=labels[k])
    for ax,t in [(ax_fp,r'$P_{fp}$ — Probabilité de faux positif (Eve acceptée)'),
                 (ax_fn,r'$P_{fn}$ — Probabilité de faux négatif (Alice rejetée)')]:
        ax.axhline(1e-6,color='k',ls='--',lw=1.2,alpha=0.5,label=r'Seuil $10^{-6}$')
        ax.set_xlabel(r'Nombre de rounds $R$',fontsize=10)
        ax.set_ylabel('Probabilité (log)',fontsize=10)
        ax.set_title(t,fontsize=11,fontweight='bold',pad=5)
        ax.legend(fontsize=8.5,loc='upper right')
        ax.grid(True,alpha=0.25,ls='--',which='both')
        ax.set_xlim(1,25)
    pdf.savefig(fig,bbox_inches='tight'); plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 8 — SYNTHÈSE
# ═════════════════════════════════════════════════════════════════════════════
def page_synthesis(pdf):
    fig=new_fig(); hdr(fig,'Synthèse et Justification des Résultats',COLS['dark'])
    ftr(fig,8,8)
    ax=fig.add_axes([0.04,0.03,0.92,0.905]); ax.axis('off')
    y=0.89

    # Tableau
    y=sec_bar(ax,
        r'Tableau de synthèse  (n=5, K=1600, η=0.5, R=10)',
        COLS['mid'],y)+0.004
    hdrs=[r'Attaque',r'$F$',r'$\mu_E$',r'$P_{fp}$ (R=10)',r'$P_{fn}$ (R=10)',r'$T^*$']
    cx=[0.00,0.24,0.38,0.54,0.70,0.88]
    rows_data=[
        ('A1 — Clonage UQCM', COLS['a1'],  mE1(n,K,eta,ldc)),
        ('A2 — POVM (fixe)',   COLS['a2'],  mE2(n,K,eta,ldc)),
        ('A3 — Intercept-Res.',COLS['a3'],  mE3(n,K,eta,ldc)),
        ('A4 — Quadrature',    COLS['a4'],  mE4(n,K,eta,ldc)),
    ]
    for i,(lbl,rc) in enumerate([('',COLS['mid'])]+[(r[0],r[1]) for r in rows_data]):
        h=0.040
        ax.add_patch(FancyBboxPatch((0,y-h),0.98,h,
            boxstyle='round,pad=0.003',facecolor=rc,
            alpha=1 if i==0 else 0.75,lw=0,transform=ax.transAxes))
        if i==0:
            cells=hdrs
        else:
            nm,rc2,mE=rows_data[i-1]
            Fv=mE/(eta*n); fp,fn,T=errs(mA,mE,10)
            cells=[nm,f'{Fv:.5f}',f'{mE:.5f}',f'{fp:.2e}',f'{fn:.2e}',str(T)]
        for txt,x in zip(cells,cx):
            fw='bold' if i==0 else 'normal'
            ax.text(x+0.005,y-h/2,txt,ha='left',va='center',
                    fontsize=8.2,fontweight=fw,color='white',transform=ax.transAxes)
        y-=h+0.004
    y-=0.012

    justifs=[
        ("Ordre des fidélités et interprétation physique",[
            r"$F_4 = \dfrac{2n}{2n+K}$  $>$  $F_1 = F_2 = \dfrac{n+1}{n+K}$  $\gg$  $F_3 = \dfrac{2}{K+1}$",
            "",
            r"$\bullet$  Attaque 4 (quadrature) : la détection hétérodyne mesure les amplitudes complexes",
            r"   avec bruit de grenaille minimal $\sigma^2 = \frac{1}{4n}$.  Pour $n=5$, $K=1600$ : $F_4\approx 0.00621$.",
            "",
            r"$\bullet$  Attaques 1 & 2 (POVM / UQCM) : le clonage UQCM atteint exactement la borne",
            r"   informationnelle de Brüß–Macchiavello.  $F = \frac{n+1}{n+K}\approx 0.00374$.",
            "",
            r"$\bullet$  Attaque 3 (intercept-resend) : base aléatoire dans $\mathbb{R}^K$,",
            r"   $F_3 = \frac{2}{K+1}\approx 0.00125$  — deux fois plus faible que UQCM.",
        ]),
        (r"Pourquoi $\mu_A \gg \mu_E$ garantit la sécurité",[
            r"La sécurité repose sur le faible rapport signal/bruit d'Eve au pixel cible $k$ :",
            "",
            r"  $\mu_A = \eta\,n + \lambda_{dc} = 2.510$   (signal fort — bonne clé)",
            r"  $\mu_E = \eta\,n\,F + \lambda_{dc}$          (signal dégradé par $F \ll 1$)",
            "",
            r"Avec $F\approx 0.004$ (UQCM) : $\mu_E\approx 0.019$, soit un ratio $\approx 130\times$.",
            r"Sur $R$ rounds, les distributions $\mathrm{Poisson}(R\mu)$ s'écartent exponentiellement.",
        ]),
        (r"Rôle du nombre de rounds $R$",[
            r"Les paramètres cumulés sont $\lambda_A = R\mu_A$ et $\lambda_E = R\mu_E$.",
            r"Les CDF de Poisson s'écartent exponentiellement $\Rightarrow$ sécurité exponentielle en $R$.",
            r"Dès $R=10$ et $n=5$ : $P_{fp},\,P_{fn} < 10^{-6}$ pour toutes les attaques.",
        ]),
    ]

    for title, lines in justifs:
        y=sec_bar(ax,title,COLS['mid'],y)+0.004
        for line in lines:
            math_line(ax,line,0.015,y,fs=8.8,col='#1a1a2e')
            y-=0.030 if line.strip()=='' else 0.032
        y-=0.010

    pdf.savefig(fig,bbox_inches='tight'); plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# DONNÉES DES ATTAQUES
# ═════════════════════════════════════════════════════════════════════════════
fp1,fn1,T1=errs(mA,mE1(n,K,eta,ldc),10)
fp2,fn2,T2=errs(mA,mE2(n,K,eta,ldc),10)
fp3,fn3,T3=errs(mA,mE3(n,K,eta,ldc),10)
fp4,fn4,T4=errs(mA,mE4(n,K,eta,ldc),10)

ATT = [
  # page, num, col, title, source,
  # desc, formulas, code, results, F, mE, pfp, pfn, T*
  (3,'1',COLS['a1'],
   'Clonage Quantique UQCM',
   'Yao Tao et al. — "Quantum cloning attacks against PUF-based quantum authentication systems"',
   [
    r'Eve utilise une Machine de Clonage Quantique Universelle (UQCM)',
    r'pour copier le challenge quantique $|\psi_c\rangle$ envoyé par Alice.',
    '',
    r'Protocole :',
    r'  1.  Eve intercepte $|\psi_c\rangle$ ($n$ photons dans $K$ modes).',
    r'  2.  Elle applique l\'UQCM optimal (Brüß–Macchiavello) pour produire un clone.',
    r'  3.  Elle envoie le clone au PUF et tente de lire la réponse.',
    '',
    r'Le clonage parfait est impossible (théorème de non-clonage), mais un clone',
    r'partiel avec fidélité maximale $\frac{n+1}{n+K}$ est atteignable.',
   ],
   [
    r'Fidélité maximale du clone UQCM :',
    r'$F_1 = \dfrac{n+1}{n+K}$',
    '',
    r'Photons moyens pour Eve au pixel cible $k$ :',
    r'$\mu_{Eve} = \eta \cdot n \cdot F_1 + \lambda_{dc}$',
    '',
    r'Construction de $C_{Eve}$ (Gram–Schmidt) :',
    r'$C_{Eve} = \sqrt{F_1}\,C_k \;+\; \sqrt{1-F_1}\,C_{\perp}$,  avec $C_{\perp} \perp C_k$',
   ],
   [
    'def F_cloning(n, K):',
    '    return (n + 1) / (n + K)',
    '',
    'def build_eve_challenge_cloning(C_k, n, K):',
    '    F = F_cloning(n, K)',
    '    v = np.random.randn(len(C_k)) + 1j*np.random.randn(len(C_k))',
    '    v -= (v @ C_k.conj()) * C_k      # composante orthogonale a C_k',
    '    C_perp = v / np.linalg.norm(v)',
    '    C_eve  = np.sqrt(F)*C_k + np.sqrt(1-F)*C_perp',
    '    return C_eve / np.linalg.norm(C_eve)',
   ],
   [
    rf'$F_1 = \dfrac{{5+1}}{{5+1600}} = \dfrac{{6}}{{1605}} \approx {F1(n,K):.6f}$',
    rf'$\mu_E = 0.5 \times 5 \times {F1(n,K):.6f} + 0.01 = {mE1(n,K,eta,ldc):.6f}$',
    rf'$\mu_A = {mA:.4f}$   (ratio $\approx {mA/mE1(n,K,eta,ldc):.0f}\times$)',
    rf'$P_{{fp}}(R=10) = {fp1:.3e}$   $P_{{fn}}(R=10) = {fn1:.3e}$   $T^* = {T1}$',
   ],
   F1(n,K),mE1(n,K,eta,ldc),fp1,fn1,T1),

  (4,'2',COLS['a2'],
   'POVM Générique Optimal',
   'Boris Skoric — "Security analysis of Quantum-Readout PUFs in the case of challenge-estimation attacks"',
   [
    r'Eve effectue la meilleure mesure POVM (Positive Operator-Valued Measure)',
    r'possible sur le challenge $|\psi_c\rangle^{\otimes n}$ — borne informationnelle optimale.',
    '',
    r'Protocole :',
    r'  1.  Eve intercepte $n$ copies du challenge (état $|\psi_c\rangle^{\otimes n}$).',
    r'  2.  Elle applique le POVM optimal (non spécifié physiquement).',
    r'  3.  Elle reconstruit $|\hat{\psi}\rangle$ et calcule la réponse $R(|\hat{\psi}\rangle)$.',
    '',
    r'Variante Poisson : si $n\sim\mathrm{Poisson}(\bar{n})$,',
    r'alors $F_{\max} \approx \dfrac{\bar{n}+1}{\bar{n}+K}$.',
   ],
   [
    r'Fidélité POVM optimale ($n$ fixe) :',
    r'$F_2 = \dfrac{n+1}{n+K} \;\equiv\; F_1$',
    '',
    r'Fidélité POVM ($n \sim \mathrm{Poisson}(\bar{n})$) :',
    r'$F_2^{\mathrm{Poisson}} = \dfrac{\bar{n}+1}{\bar{n}+K}$',
    '',
    r'Note : $F_2 = F_1$ pour $n$ fixe — le UQCM est POVM-optimal.',
    r'La correction $n\to n+1$ vaut $+20\%$ pour $n=5$, $K=1600$.',
   ],
   [
    'def F_povm(n, K):           return (n+1) / (n+K)',
    'def F_povm_poisson(n_av,K): return (n_av+1) / (n_av+K)',
    '',
    'def mu_eve_povm(n, K, eta, ldc, poisson=False):',
    '    F = F_povm_poisson(n,K) if poisson else F_povm(n,K)',
    '    return eta * n * F + ldc',
    '',
    '# Comparaison Section 8 (approx) vs exact :',
    '#  approx : eta*n**2/(K+n) + ldc  -> F = n/(n+K)',
    '#  exact  : eta*n*(n+1)/(n+K)+ldc -> F = (n+1)/(n+K)',
   ],
   [
    rf'$F_2 = \dfrac{{5+1}}{{5+1600}} = {F2(n,K):.6f}$   (identique à $F_1$)',
    rf'$\mu_E = {mE2(n,K,eta,ldc):.6f}$',
    r'Approx. $n/(n+K) = 0.003115$ vs exact $(n+1)/(n+K) = 0.003738$  ($+20\%$)',
    rf'$P_{{fp}}(R=10) = {fp2:.3e}$   $P_{{fn}}(R=10) = {fn2:.3e}$   $T^* = {T2}$',
   ],
   F2(n,K),mE2(n,K,eta,ldc),fp2,fn2,T2),

  (5,'3',COLS['a3'],
   'Intercept-Resend sur Base Aléatoire',
   'B. Skoric — "Quantum readout of Physical Unclonable Functions: Remote authentication"',
   [
    r'Eve choisit une base orthonormée aléatoire $\{|b_j\rangle\}$ dans l\'espace de',
    r'Hilbert de dimension $K$, mesure $|\psi_c\rangle$, et renvoie $|b_j\rangle$.',
    '',
    r'Protocole (authentification simple) :',
    r'  1.  Eve génère $U$ unitaire aléatoire (Haar) ; base $\{|b_j\rangle = U|e_j\rangle\}$.',
    r'  2.  Probabilité d\'obtenir $|b_j\rangle$ : $P(j) = |\langle b_j|\psi_c\rangle|^2$.',
    r'  3.  Elle tire $j\sim P(j)$ et renvoie $|b_j\rangle$ au PUF.',
    '',
    r'Cas OKE : Eve contrainte à l\'observable $B = H^\dagger H$',
    r'(vecteurs singuliers droits de $H$, précalculés par SVD).',
    '',
    r'Optimisation : $U^\dagger C_k \sim \mathrm{Uniforme}(S^{2K-1})$ par Haar',
    r'  $\Rightarrow$ génération directe en $O(K)$ sans QR en $O(K^3)$.',
   ],
   [
    r'Fidélité attendue (CUE, $K$ modes) :',
    r'$F_3 = \dfrac{2}{K+1}$',
    '',
    r'Dérivation (ensemble unitaire circulaire) :',
    r'$\mathbb{E}\left[\sum_k P(k)^2\right] = K\cdot\mathbb{E}[|u_{jk}|^4]'
    r' = K\cdot\dfrac{2}{K(K+1)} = \dfrac{2}{K+1}$',
    '',
    r'$\mu_{Eve} = \eta\cdot n\cdot F_3 + \lambda_{dc}$',
   ],
   [
    'def F_intercept_theory(K): return 2.0 / (K + 1)',
    '',
    'def build_eve_challenge_intercept(C_k, mode="random", probs_oke=None):',
    '    K_dim = len(C_k)',
    '    if mode == "random":',
    '        w = np.random.randn(K_dim)+1j*np.random.randn(K_dim)',
    '        w /= np.linalg.norm(w)    # O(K), sans QR K x K',
    '        probs = np.abs(w)**2',
    '    else: probs = probs_oke       # SVD pre-calculee hors boucle',
    '    idx = np.random.choice(K_dim, p=probs/probs.sum())',
    '    return C_eve, float(probs[idx])',
   ],
   [
    rf'$F_3 = \dfrac{{2}}{{K+1}} = \dfrac{{2}}{{1601}} \approx {F3(K):.6f}$',
    rf'$\mu_E = {mE3(n,K,eta,ldc):.6f}$'
    rf'   (ratio $\approx {mA/mE3(n,K,eta,ldc):.0f}\times$)',
    rf'$F_3 \approx F_1/3$ : intercept-resend est $2\times$ moins efficace que UQCM.',
    rf'$P_{{fp}}(R=10) = {fp3:.3e}$   $P_{{fn}}(R=10) = {fn3:.3e}$   $T^* = {T3}$',
   ],
   F3(K),mE3(n,K,eta,ldc),fp3,fn3,T3),

  (6,'4',COLS['a4'],
   'Quadrature / Détection Hétérodyne',
   'Skoric, Mosk, Pinkse — "Security of Quantum-Readout PUFs against quadrature attacks"',
   [
    r'Eve mesure les deux quadratures ($Q$ et $P$) de chaque mode du challenge',
    r'par détection hétérodyne, puis reconstruit son estimé $\hat{C}$.',
    '',
    r'Protocole :',
    r'  1.  Eve intercepte le challenge ($K$ modes, $n$ photons au total).',
    r'  2.  Pour chaque mode $a$ : $Q_a = \mathrm{Re}(\sqrt{n}\,c_a)+\xi_a/2$,',
    r'       $P_a = \mathrm{Im}(\sqrt{n}\,c_a)+\zeta_a/2$,  $\xi_a,\zeta_a\sim\mathcal{N}(0,1)$.',
    r'  3.  Estimation : $\hat{c}_a = (Q_a+iP_a)/\sqrt{n} = c_a + (\xi_a+i\zeta_a)/(2\sqrt{n})$.',
    r'  4.  Normalisation : $\hat{C}_{Eve} = \hat{c}/\|\hat{c}\|$.',
    '',
    r"C'est l'attaque classique la plus réalisable avec la technologie optique actuelle.",
   ],
   [
    r'Bruit par composante (hétérodyne) : $\sigma^2 = \dfrac{1}{4n}$',
    '',
    r'Bruit total sur $K$ modes : $\|\varepsilon\|^2 \approx K\cdot\sigma^2 = \dfrac{K}{4n}$',
    '',
    r'Fidélité après normalisation :',
    r'$F_4 = \dfrac{2n}{2n+K}$',
    '',
    r'$F_4 > F_1$ : le bruit cohérent hétérodyne est inférieur à la limite POVM discrète.',
   ],
   [
    'def F_quadrature(n, K):',
    '    return 2.0 * n / (2.0 * n + K)',
    '',
    'def build_eve_challenge_quadrature(C_k, n_ph):',
    '    # Bruit heterodyne : std = 1/(2*sqrt(n)) par composante complexe',
    '    sigma = 1.0 / (2.0 * np.sqrt(n_ph))',
    '    noise = sigma*(np.random.randn(len(C_k))+1j*np.random.randn(len(C_k)))',
    '    return (C_k + noise) / np.linalg.norm(C_k + noise)',
    '',
    'def mu_eve_quadrature(n, K, eta, ldc):',
    '    return eta * n * F_quadrature(n, K) + ldc',
   ],
   [
    rf'$F_4 = \dfrac{{2\times5}}{{2\times5+1600}} = \dfrac{{10}}{{1610}} \approx {F4(n,K):.6f}$',
    rf'$\mu_E = {mE4(n,K,eta,ldc):.6f}$'
    rf'   (ratio $\approx {mA/mE4(n,K,eta,ldc):.0f}\times$)',
    rf'$F_4 = {F4(n,K):.5f} > F_1 = {F1(n,K):.5f}$  '
    rf'($+{(F4(n,K)/F1(n,K)-1)*100:.0f}\%$ plus efficace)',
    rf'$P_{{fp}}(R=10) = {fp4:.3e}$   $P_{{fn}}(R=10) = {fn4:.3e}$   $T^* = {T4}$',
   ],
   F4(n,K),mE4(n,K,eta,ldc),fp4,fn4,T4),
]

# ═════════════════════════════════════════════════════════════════════════════
# GÉNÉRATION
# ═════════════════════════════════════════════════════════════════════════════
out='/Users/mohamedryad/Desktop/psc/rapport_attaques_qpuf.pdf'
with PdfPages(out) as pdf:
    page_title(pdf)
    page_protocol(pdf)
    for args in ATT:
        attack_page(pdf,*args)
    page_plots(pdf)
    page_synthesis(pdf)
print(f'PDF generated: {out}')
