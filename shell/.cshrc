# .cshrc

# User specific aliases and functions

alias rm 'rm -i'
alias cp 'cp -i'
alias mv 'mv -i'

alias lh   'ls -lh'
alias cd   'cd \!*; ls'
alias ..   'cd ../'
alias go   'cd /root/work/sts'

alias gits 'git status'

alias buildvnc 'vncserver -geometry 2540x1360'


setenv PATH "/usr/local/git/bin:$PATH"

#du -lh --max-depth=1
#git rebase -i HEAD~2
#netstat -ltnp | grep vnc
