for file in $(ls -p /media/ravirajukrishna/My\ Passport/result_json1 | grep -v / | tail -5000)
do
mv /media/ravirajukrishna/My\ Passport/result_json1/$file /media/ravirajukrishna/My\ Passport/$1/
done
