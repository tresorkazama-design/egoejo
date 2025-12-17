# 🎨 Génération de l'Image Open Graph

## Option 1 : Utiliser le générateur HTML (Recommandé)

1. Ouvrez le fichier `public/og-image-generator.html` dans votre navigateur
2. Cliquez sur "Générer l'image"
3. Cliquez sur "Télécharger l'image"
4. Renommez le fichier téléchargé en `og-image.jpg`
5. Placez-le dans le dossier `public/`

## Option 2 : Utiliser l'image SVG existante

L'image SVG (`public/og-image.svg`) peut être utilisée directement, mais pour une meilleure compatibilité avec tous les réseaux sociaux, il est recommandé d'utiliser un JPG.

### Convertir SVG en JPG

**Avec ImageMagick** (si installé) :
```bash
magick convert -background white -resize 1200x630 public/og-image.svg public/og-image.jpg
```

**Avec Inkscape** (si installé) :
```bash
inkscape --export-filename=public/og-image.jpg --export-width=1200 --export-height=630 public/og-image.svg
```

**En ligne** :
- Utilisez un convertisseur en ligne comme [CloudConvert](https://cloudconvert.com/svg-to-jpg)
- Téléchargez le SVG et convertissez-le en JPG 1200x630px

## Option 3 : Créer manuellement

Créez une image de **1200x630 pixels** avec :
- Fond : Dégradé vert (#00ffa3 vers #00cc82)
- Texte principal : "EGOEJO" en blanc, gras, 72px
- Sous-titre : "Collectif pour le vivant" en blanc, 32px
- Description : "Relier des citoyens à des projets sociaux à fort impact" en blanc, 24px
- Tagline : "Habiter la Terre autrement, ensemble." en blanc, 20px, italique

## Vérification

Une fois l'image créée, vérifiez qu'elle est accessible à :
- `http://localhost:5173/og-image.jpg` (en développement)
- `https://egoejo.org/og-image.jpg` (en production)

## Test

Testez l'image avec :
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)
- [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)

