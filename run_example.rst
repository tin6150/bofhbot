/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python3   bofhbot.py | tee bofhbot.BRC.2024.0203a

# current config run cmd:

module load python/3.6
./bofhbot.py | tee bofhbot.BRC.2018.1001.txt

./bofhbot.py -ddd 
./bofhbot.py --ipmi -v 
./bofhbot.py -vv -ddd --nodelist ./dev_aid/nodelist

./bofhbot.py -ddddd -s ./dev_aid/sample_input/sinfo-RSE.test.txt







**^ tin ln000.brc ~ ^**>  env | grep -i python
MANPATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/share/man:/global/software/sl-7.x86_64/modules/tools/git/2.11.1/share/man:/global/software/sl-7.x86_64/modules/tools/emacs/25.1/share/man:/global/software/sl-7.x86_64/modules/tools/vim/7.4/share/man:/usr/share/man
LIBRARY_PATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/lib
PYTHON_DIR=/global/software/sl-7.x86_64/modules/langs/python/3.6
FPATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/include
CPATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/include
PATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/bin:/global/software/sl-7.x86_64/modules/tools/git/2.11.1/bin:/global/software/sl-7.x86_64/modules/tools/emacs/25.1/bin:/global/software/sl-7.x86_64/modules/tools/vim/7.4/bin:/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin:/global/home/groups/allhands/bin:/global/home/groups/scs/tin:/global/home/users/tin/bin
_LMFILES_=/global/software/sl-7.x86_64/modfiles/tools/vim/7.4:/global/software/sl-7.x86_64/modfiles/tools/emacs/25.1:/global/software/sl-7.x86_64/modfiles/tools/git/2.11.1:/global/software/sl-7.x86_64/modfiles/langs/python/3.6
MODULEPATH=/global/software/sl-7.x86_64/modfiles/langs:/global/software/sl-7.x86_64/modfiles/tools:/global/software/sl-7.x86_64/modfiles/apps:/global/home/groups/consultsw/sl-7.x86_64/modfiles:/global/home/users/tin/CF_BK/SMFdev/modfiles/:/global/software/sl-7.x86_64/modfiles/python/3.6
LOADEDMODULES=vim/7.4:emacs/25.1:git/2.11.1:python/3.6
PKG_CONFIG_PATH=/global/software/sl-7.x86_64/modules/langs/python/3.6/lib/pkgconfig
INCLUDE=/global/software/sl-7.x86_64/modules/langs/python/3.6/include


