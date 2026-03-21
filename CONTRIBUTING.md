 Create a New Feature Branch and Push Changes

```bash
git clone https://github.com/nickjanssens-dev/HEXSTORM.git
cd HEXSTORM
git switch -c reviews-page

# edit files

git add .
git commit -m "Added reviews page"
git push -u origin reviews-page

# change your current setup to include all files

git fetch origin
git merge origin
