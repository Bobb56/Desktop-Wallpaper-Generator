from random import *
from math import *
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import threading
import sys

'''
PROCEDE :
1- Générer une image aléatoirement
2- Appliquer successivement :
    - un flou de l'image
    - une multiplication des couleurs
De manière à faire grossir les symboles

'''


class Process:

    def aff(self, value):
        '''Affiche le pourcentage de chargement correspondant à value'''
        percent = int((value - self.debut)/self.fin * 100) + 1

        if percent > self.percent:
            self.percent = percent

            print("\033[2K\033[A", end='')


            print(self.percent, '% effectué')

            self.previous = len(str(self.percent)) + 11


    def __init__(self, message, debut, fin):
        '''initialise un objet de classe Process'''
        self.debut = debut
        self.fin = fin
        self.previous = 0
        self.percent = 0
        print(message + '\n')
    
    def end(self):
        print("\033[2K\033[A")







# VARIABLE GLOBALE CONTENANT LE PRECEDENT NOMBRE ALEATOIRE


def tuple_int(t):
    return (int(t[0]), int(t[1]), int(t[2]))



def save_image(rgb_array, filename):
    """
    Sauvegarde un tableau 2D de couleurs RGB dans un fichier PNG.
    
    :param rgb_array: Liste de listes contenant des tuples RGB.
    :param filename: Nom du fichier PNG de sortie.
    """
    # Obtenir les dimensions de l'image
    height = len(rgb_array)
    width = len(rgb_array[0])

    # Créer une nouvelle image avec les dimensions spécifiées
    image = Image.new("RGB", (width, height))

    # Charger les pixels de l'image avec les valeurs RGB du tableau
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), tuple_int(rgb_array[y][x]))

    # Sauvegarder l'image dans un fichier PNG
    image.save(filename)




def next_number():
    global PREVIOUS_NUMBER
    PREVIOUS_NUMBER = (PREVIOUS_NUMBER + 7) * 82589933 % 256
    return PREVIOUS_NUMBER










def ran_couleur():
    return (randint(0, 256), randint(0, 256), randint(0, 256))


add = lambda c1, c2 : (c1[0] + c2[0], c1[1] + c2[1], c1[2] + c2[2])
mul = lambda x1, x2 : (x1 * x2[0], x1 * x2[1], x1 * x2[2]) if type(x1) in [int, float]  else (x2 * x1[0], x2 * x1[1], x2 * x1[2])
mod = lambda c : (c[0]%256, c[1]%256, c[2]%256)
remove_zero = lambda c : ((c[0] == 0)*1 + c[0], (c[1] == 0)*1 + c[1], (c[2] == 0)*1 + c[2])




def image_ranGen(hauteur, largeur):
    return [[ran_couleur() for j in range(largeur)] for i in range(hauteur)]




def dim(image): # hauteur, largeur
    return (len(image), len(image[0]))


def image_vide(image):
    hauteur, largeur = dim(image)
    return [[None for j in range(largeur)] for i in range(heuteur)]








def split_rgb_channels(image):
    height = len(image)
    width = len(image[0])

    red_channel = [[0]*width for _ in range(height)]
    green_channel = [[0]*width for _ in range(height)]
    blue_channel = [[0]*width for _ in range(height)]

    for i in range(height):
        for j in range(width):
            red_channel[i][j] = image[i][j][0]
            green_channel[i][j] = image[i][j][1]
            blue_channel[i][j] = image[i][j][2]

    return red_channel, green_channel, blue_channel

def apply_gaussian_blur(image, sigma):
    image_array = np.array(image)
    blurred_image = gaussian_filter(image_array, sigma=sigma)
    return blurred_image

def combine_rgb_channels(red_channel, green_channel, blue_channel):
    height = len(red_channel)
    width = len(red_channel[0])

    image = [[(0, 0, 0)] * width for _ in range(height)]

    for i in range(height):
        for j in range(width):
            image[i][j] = (int(red_channel[i][j]), int(green_channel[i][j]), int(blue_channel[i][j]))

    return image


def gaussian_blur_rgb_image(image, sigma):
    red_channel, green_channel, blue_channel = split_rgb_channels(image)
    
    blurred_red_channel = [None]
    blurred_green_channel = [None]
    blurred_blue_channel = [None]

    def blur_channel(channel, sigma, result):
        result[0] = apply_gaussian_blur(channel, sigma)

    red_thread = threading.Thread(target=blur_channel, args=(red_channel, sigma, blurred_red_channel))
    green_thread = threading.Thread(target=blur_channel, args=(green_channel, sigma, blurred_green_channel))
    blue_thread = threading.Thread(target=blur_channel, args=(blue_channel, sigma, blurred_blue_channel))

    red_thread.start()
    green_thread.start()
    blue_thread.start()

    red_thread.join()
    green_thread.join()
    blue_thread.join()
    blurred_image = combine_rgb_channels(blurred_red_channel[0], blurred_green_channel[0], blurred_blue_channel[0])
    return blurred_image







def iter(image, fonction):
    return [[fonction(x) for x in ligne] for ligne in image]





def generer(width, height, K, n):
    taille = sqrt(height*width)

    if taille <= 100 or n < 3: # cas de base
        print(f"Génération d'une image initiale aléatoire de taille {width}x{height}...")
        image = image_ranGen(height, width)
        
        #on effectue n itérations
        for i in range(1,n):
            image = gaussian_blur_rgb_image(image, i*taille/K)
            
            image = iter(image, lambda couleur : mul(2 + 5*(n-i)/n,couleur))
            image = iter(image, mod)
            image = iter(image, remove_zero)
        
    else:
        image = generer(width//2, height//2, K, n-3)
        
        # on agrandit l'image
        print(f"Agrandissement de l'image en {width}x{height}...")
        image = [[image[x//2][y//2] for y in range(len(image[0])*2)] for x in range(len(image)*2)]
        
        # on effectue trois itérations
        print("Affinage de l'image...")
        
        for i in range(n-3,n):
            image = gaussian_blur_rgb_image(image, i*taille/K)
            
            image = iter(image, lambda couleur : mul(2 + 5*(n-i)/n,couleur))
            image = iter(image, mod)
            image = iter(image, remove_zero)

    return image




def main(args):
    
    width = 1920
    height = 1080
    # plus K est grand, plus les symboles que l'on va observer seront petits
    # apparition des symboles : 100
    # mélange de flou et de taches : 400 et +

    # traitement des arguments

    if len(args) > 2 and args[1][0:2] == 'K=':
        K = int(args[1][2:])
        name = args[2]
    elif len(args) > 2 and args[2][0:2] == 'K=':
        K = int(args[2][2:])
        name = args[1]
    else:
        K = 110
        name = args[1]
    
    n = max(5,int(3000/K)) # calcul d'un nombre d'itérations en fonction de la taille des objets
    
    image = generer(width, height, K, n)

    save_image(image, name)
    
    print("Terminé !")



if __name__ == '__main__':
    '''for i in range(1, 15):
        K = 'K=' + str(randint(100, 110))
        main(['ranimg.py', K, 'image' + str(i) + '.png'])'''
    
    main(sys.argv)
