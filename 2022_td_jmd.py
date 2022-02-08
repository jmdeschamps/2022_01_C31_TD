from tkinter import *
import time
import helper


class Vue():
    def __init__(self, parent):
        self.parent = parent
        self.modele = self.parent.modele
        self.root = Tk()
        self.root.title("Carre Rouge, alpha_0.1")
        self.cadres = self.creer_interface()

    def creer_interface(self):
        # cadre HUD affichant la duree
        self.cadre_info = Frame(self.root, bg="lightgreen")
        self.var_duree = StringVar()
        label_duree = Label(self.cadre_info, text="0", textvariable=self.var_duree)
        label_duree.pack()
        btn_demarrer = Button(self.cadre_info, text="DEMARRER", command=self.parent.debuter_partie)
        btn_demarrer.pack()
        # le canevas de jeu
        self.canevas = Canvas(self.root, width=self.modele.largeur, height=self.modele.hauteur, bg="white")
        # visualiser
        self.cadre_info.pack(expand=1, fill=X)
        self.canevas.pack()

        self.canevas.bind("<Button>",self.creer_tour)

        self.afficher_partie()

    def creer_tour(self,evt):
        x=evt.x
        y=evt.y
        self.parent.creer_tour(x,y)

    def debuter_partie(self, evt):
        self.canevas.tag_unbind("pion", "<Button>")
        self.canevas.bind("<B1-Motion>", self.recibler_pion)
        self.canevas.bind("<ButtonRelease>", self.arreter_jeu)
        self.parent.debuter_partie()

    def arreter_jeu(self, evt):
        self.parent.partie_en_cours = 0
        self.canevas.tag_bind("pion", "<Button>", self.debuter_partie)
        self.canevas.unbind("<B1-Motion>")
        self.canevas.unbind("<ButtonRelease>")

    def afficher_partie(self):
        self.canevas.delete("mobile")
        for i in self.modele.partie.creeps_en_jeu:
            self.canevas.create_oval(i.x-i.demitaille,i.y-i.demitaille,
                                     i.x+ i.demitaille, i.y+ i.demitaille,fill=i.couleur,tags=("mobile",))

        for j in self.modele.partie.tours:
            for i in j.projectiles:
                self.canevas.create_oval(i.x - i.demitaille, i.y - i.demitaille,
                                         i.x + i.demitaille, i.y + i.demitaille, fill=i.couleur, tags=("mobile",))


    def afficher_tour(self,tour):
        self.canevas.create_rectangle(tour.x-tour.demi_largeur,tour.y-tour.demi_hauteur,
                                      tour.x+tour.demi_largeur,tour.y+tour.demi_hauteur,
                                      fill="purple")
    def afficher_chemin(self):
        for i in self.modele.partie.chemins:
            self.canevas.create_line(i[0],i[1],fill="red",width=30)

class Modele():
    def __init__(self, parent):
        self.parent = parent
        self.largeur = 800
        self.hauteur = 600
        self.partie =Partie(self)

    def creer_tour(self,x,y):
        rep=self.partie.creer_tour(x,y)
        return rep

    def jouer_tour(self):
        self.partie.jouer_tour()

class Partie():
    def __init__(self, parent):
        self.parent = parent
        self.largeur = self.parent.largeur
        self.hauteur = self.parent.hauteur
        self.nivo=0
        self.nbparnivo=10
        self.creeps_en_attente = []
        self.creeps_en_jeu=[]
        self.tours = []
        self.morts=[]
        self.delaicreepmax=50
        self.delaicreep=0
        self.chemins=[
                      [[0, 200], [200, 50]],
                      [[200,50],[400,50]],
                      [[400, 50], [400, 500]],
                      [[400, 500], [500, 500]],
                      [[500, 500], [500, 300]],
                      [[500, 300],[800,300]]]
        self.creernivo()

    def creer_tour(self,x,y):
        tour=Tour(self,x,y)
        self.tours.append(tour)
        return tour

    def creernivo(self):
        self.nivo+=1
        self.creeps=[]
        for i in range(self.nivo*self.nbparnivo):
            self.creeps_en_attente.append(Creep(self))

    def jouer_tour(self):
        if self.delaicreep==0 and self.creeps_en_attente:
            creep=self.creeps_en_attente.pop()
            creep.trouver_prochain_troncon()
            self.creeps_en_jeu.append(creep)
            self.delaicreep=self.delaicreepmax
        else:
            self.delaicreep-=1

        for i in self.creeps_en_jeu:
            i.avancer()

        for i in self.tours:
            i.jouer_tour()

        for i in self.morts:
            if i in self.creeps_en_jeu:
                self.creeps_en_jeu.remove(i)
        self.morts=[]


class Creep():
    def __init__(self, parent):
        self.parent = parent
        self.x = 0
        self.y = 0
        self.ciblex=None
        self.cibley=None
        self.angle=0
        self.prochaintroncon=0
        self.vitesse=5
        self.mana=100
        self.demitaille = 16
        self.couleur="green"

    def demarrer_attaque(self):
        self.trouver_prochain_troncon()

    def trouver_prochain_troncon(self):
        if self.prochaintroncon<len(self.parent.chemins):
            debut,fin=self.parent.chemins[self.prochaintroncon]
            self.x =debut[0]
            self.y =debut[1]
            self.ciblex=fin[0]
            self.cibley=fin[1]

            self.prochaintroncon+=1
            self.angle=helper.Helper.calcAngle(self.x,self.y,self.ciblex,self.cibley)

    def avancer(self):
        x,y=helper.Helper.getAngledPoint(self.angle,self.vitesse,self.x,self.y)
        dist=helper.Helper.calcDistance(x,y,self.ciblex,self.cibley)
        if dist<self.vitesse:
            self.trouver_prochain_troncon()
        else:
            self.x=x
            self.y=y

    def blesser(self,force):
        self.mana-=force
        if self.mana<1:
            self.parent.morts.append(self)

class Tour():
    def __init__(self, parent,x,y):
        self.parent = parent
        self.x = x
        self.y = y
        self.etendue=100
        self.delai_attaque=0
        self.delai_attaque_max=6
        self.demi_largeur = 10
        self.demi_hauteur=30
        self.projectiles=[]
        self.morts=[]

    def jouer_tour(self):
        for i in self.parent.creeps_en_jeu:
            dist=helper.Helper.calcDistance(self.x,self.y,i.x,i.y)
            if dist<self.etendue and self.delai_attaque<1:
                self.projectiles.append(Obus(self,i))
                self.delai_attaque=self.delai_attaque_max
            else:
                self.delai_attaque-=1
        for i in self.projectiles:
            i.avancer()

        for i in self.morts:
            self.projectiles.remove(i)
        self.morts=[]

class Obus():
    def __init__(self,parent,cible):
        self.parent=parent
        self.x=self.parent.x
        self.y=self.parent.y
        self.ciblex=cible.x
        self.cibley=cible.y
        self.cible=cible
        self.demitaille=3
        self.vitesse=10
        self.couleur="orange"
        self.force=10
        self.angle=helper.Helper.calcAngle(self.x,self.y,self.ciblex,self.cibley)

    def avancer(self):
        x,y=helper.Helper.getAngledPoint(self.angle,self.vitesse,self.x,self.y)
        dist = helper.Helper.calcDistance(x, y, self.ciblex, self.cibley)
        if dist < self.vitesse:
            self.explose()
        else:
            self.x = x
            self.y = y

    def explose(self):
        self.cible.blesser(self.force)
        self.parent.morts.append(self)

class Controleur():
    def __init__(self):
        self.partie_en_cours = 0
        self.modele = Modele(self)
        self.vue = Vue(self)
        self.vue.root.mainloop()

    def recibler_pion(self, x, y):
        self.modele.recibler_pion(x, y)

    def debuter_partie(self):
        self.partie_en_cours=1
        self.vue.afficher_chemin()
        self.jouer_partie()

    def jouer_partie(self):
        if self.partie_en_cours:
            self.modele.jouer_tour()
            self.vue.afficher_partie()
            self.vue.root.after(40, self.jouer_partie)

    def creer_tour(self,x,y):
        rep=self.modele.creer_tour(x,y)
        self.vue.afficher_tour(rep)

if __name__ == '__main__':
    c = Controleur()
    print("L'application se termine")


