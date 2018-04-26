#!/bin/bash
#######################################################################################################
#######################################################################################################
#######################################################################################################
######                                                                                          #######
######                                                                                          #######
######                 This script will help you to recover the accidentally                    #######
######                     deleted data from crashed linux file systems                         #######
######                          Script created by (Srijan Kishore)                              #######
######                                                                                          #######
######                                                                                          #######
#######################################################################################################
#######################################################################################################
#######################################################################################################

# User Check

if [ "$USER" = 'root' ]
    then
        gdialog --title "User Check" --msgbox "User is root, you can execute the script successfully." 200 150
        echo "User is root, you can execute the script successfully"
    else
        gdialog --title "User Check" --msgbox "User is not Root. Please run the script as root user." 200 150
        echo "User is not Root. Please run the script as root user."
        exit 1
fi

# Check your operating system

cat /etc/debian_version >> /dev/null
if [ "$?" = 0 ]
    then
        echo "You are using ubuntu/debian"
        gdialog --title "Your Operating System" --msgbox "You are using ubuntu/debian"
    else
        gdialog --title "Your Operating System" --msgbox "You are not using debian/ubuntu.You can download the TestDisk from this link http://www.cgsecurity.org/wiki/TestDisk_Download"

    echo "You are not using debian/ubuntu. You can download the TestDisk from this link http://www.cgsecurity.org/wiki/TestDisk_Download"

fi



# Installing Testdisk
testdisk /version >> /dev/null
if [ "$?" = 0 ]
then
    echo "Testdisk already installed"
else
    echo "Installing Testdisk"
    apt-get update
    apt-get upgrade
        apt-get --force-yes -y install testdisk

                    gdialog --title "Success" --msgbox "Testdisk installed successfully" 100 50

 fi

# Set backup directory
mkdir -p /root/result/lostfiles





#Run the recovery program



photorec /d /root/result/lostfiles

# Filters files

user=`ps aux | grep gnome-session | grep -v grep | head -1 | cut -d " " -f1`
mkdir "/home/$user/recovered_output"

mkdir "/home/$user/recovered_output/Debians"
mkdir "/home/$user/recovered_output/rpms"
mkdir "/home/$user/recovered_output/conf_files"
mkdir "/home/$user/recovered_output/exe"
mkdir "/home/$user/recovered_output/binaries"
mkdir "/home/$user/recovered_output/Docs"
mkdir "/home/$user/recovered_output/Pdfs"
mkdir "/home/$user/recovered_output/Mbox"
mkdir "/home/$user/recovered_output/Images"
mkdir "/home/$user/recovered_output/Videos"
mkdir "/home/$user/recovered_output/Sound"
mkdir "/home/$user/recovered_output/ISO"
mkdir "/home/$user/recovered_output/Excel"
mkdir "/home/$user/recovered_output/Presentation"
mkdir "/home/$user/recovered_output/Web_Files"
mkdir "/home/$user/recovered_output/Archives"
mkdir "/home/$user/recovered_output/Others"

#Sorting the Recovered data


find /root/result/ -name "*.doc"    -type f  -exec mv {} "/home/$user/recovered_output/Docs/" \;
find /root/result/ -name "*.docx"   -type f  -exec mv {} "/home/$user/recovered_output/Docs/" \;
find /root/result/ -name "*.odt"    -type f  -exec mv {} "/home/$user/recovered_output/Docs/" \;
find /root/result/ -name "*.pdf"    -type f  -exec mv {} "/home/$user/recovered_output/Pdfs/" \;
find /root/result/ -name "*.mbox"   -type f  -exec mv {} "/home/$user/recovered_output/Mbox/"  \;
find /root/result/ -name "*.png"    -type f  -exec mv {} "/home/$user/recovered_output/Images/" \;
find /root/result/ -name "*.jpg"    -type f  -exec mv {} "/home/$user/recovered_output/Images/" \;
find /root/result/ -name "*.jpeg"   -type f  -exec mv {} "/home/$user/recovered_output/Images/" \;
find /root/result/ -name "*.gif"    -type f  -exec mv {} "/home/$user/recovered_output/Images/" \;
find /root/result/ -name "*.avi"    -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.mpeg"   -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.mp4"    -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.mkv"    -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.webm"   -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.wmv"    -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.flv"    -type f  -exec mv {} "/home/$user/recovered_output/Videos/" \;
find /root/result/ -name "*.mp3"    -type f  -exec mv {} "/home/$user/recovered_output/Sound/" \;
find /root/result/ -name "*.wav"    -type f  -exec mv {} "/home/$user/recovered_output/Sound/" \;
find /root/result/ -name "*.deb"    -type f  -exec mv {} "/home/$user/recovered_output/Debians/" \;
find /root/result/ -name "*.bin"    -type f  -exec mv {} "/home/$user/recovered_output/binaries/" \;
find /root/result/ -name "*.exe"    -type f  -exec mv {} "/home/$user/recovered_output/exe/" \;
find /root/result/ -name "*.rpm"    -type f  -exec mv {} "/home/$user/recovered_output/rpms/" \;
find /root/result/ -name "*.conf"    -type f  -exec mv {} "/home/$user/recovered_output/conf_files" \;
find /root/result/ -name "*.iso"    -type f  -exec mv {} "/home/$user/recovered_output/ISO/" \;
find /root/result/ -name "*.xls"    -type f  -exec mv {} "/home/$user/recovered_output/Excel/" \;
find /root/result/ -name "*.xlsx"   -type f  -exec mv {} "/home/$user/recovered_output/Excel/" \;
find /root/result/ -name "*.csv"    -type f  -exec mv {} "/home/$user/recovered_output/Excel/" \;
find /root/result/ -name "*.ods"    -type f  -exec mv {} "/home/$user/recovered_output/Excel/" \;
find /root/result/ -name "*.ppt"    -type f  -exec mv {} "/home/$user/recovered_output/Presentation/" \;
find /root/result/ -name "*.pptx"   -type f  -exec mv {} "/home/$user/recovered_output/Presentation/" \;
find /root/result/ -name "*.odp"    -type f  -exec mv {} "/home/$user/recovered_output/Presentation/" \;
find /root/result/ -name "*.html"   -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.htm"    -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.jsp"    -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.xml"    -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.css"    -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.js"     -type f  -exec mv {} "/home/$user/recovered_output/Web_Files/" \;
find /root/result/ -name "*.zip"    -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.tar"    -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.rar"    -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.gzip"   -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.tar.gz" -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.7z"     -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.bz"     -type f  -exec mv {} "/home/$user/recovered_output/Archives/" \;
find /root/result/ -name "*.bz2"    -type f  -exec mv {} "/home/$user/recovered_output/Archives" \;
find /root/result/ -name "*.*"      -type f  -exec mv {} "/home/$user/recovered_output/Others/" \;
chown -R $user "/home/$user/recovered_output"
zenity --display :0 --info --width=350 --height=100 --title "Recovery Successful" --text " Data has been recovered successfully in recovered_output folder in your home directory."
nautilus /home/$user/recovered_output &
exit 0
