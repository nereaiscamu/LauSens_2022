% Script to convert a .fig file in a .png or .jpg file with minimal white space

% It converts all .fig files in current directory to .jpg or .png files
% with several different converter techniques.
% This script aims at finding a technique removing white border around .fig file
% NOTO : You can directly export .fig file when opening it with matlab :
% See : https://fr.mathworks.com/help/matlab/creating_plots/save-figure-with-minimal-white-space.html

files = dir('*.fig');
for i=1:length(files)
   filename = files(i).name;
   new_name = extractBetween(filename, 1, (strlength(filename) - 4));
   disp(new_name{1});
   
   fig = openfig(filename, 'new');
   figure(fig);

   set(gca,'LooseInset', get(gca,'TightInset'));

   % Default call to saveas : this does NOT remove white border
   % saveas(fig, strcat(new_name{1}, 'a'), 'jpg');
   % saveas(fig, strcat(new_name{1}, 'b'), 'png');
   
   % Default call to imwrite : this does NOT remove white border
   % F = getframe(fig);
   % imwrite(F.cdata, strcat(new_name{1}, 'c', '.jpg')); % convert to a .png
   % imwrite(F.cdata, strcat(new_name{1}, 'd', '.png')); % convert to a .png

   % gca call to saveas : this does NOT remove white border
   % saveas(gca, strcat(new_name{1}, 'e'), 'jpg');
   % saveas(gca, strcat(new_name{1}, 'f'), 'png');
   
   % gcf call to imwrite : this DOES remove white border
   % WORKING
   F = getframe(gca);
   %imwrite(F.cdata, strcat(new_name{1}, 'g', '.jpg')); % convert to a .png
   imwrite(F.cdata, strcat(new_name{1}, 'h', '.png')); % convert to a .png
   
   % Default call to exportgraphics : this DOES remove (most of) white border
   % ! require matlab 2020a or greater & crash on matlab online!
   % ALMOST WORKING (a tiny white border left)
   % CAN SPECIFY PIXEL DENSITY (thus image quality)
   %exportgraphics(fig, strcat(new_name{1}, 'i', '.jpg'));
   exportgraphics(fig, strcat(new_name{1}, 'j', '.png'));

   % Default call to export_fig : NOT TESTED
   % ! require export_fig addon !
   % export_fig(strcat(new_name{1}, 'k', '.png'));
   % export_fig(strcat(new_name{1}, 'l', '.jpg'));

   % fig call to print : NOT TESTED
   % print(fig, strcat(new_name{1}, 'm'),'-dpng')
   % print(fig, strcat(new_name{1}, 'n'),'-djpg')

   % gcf call to print : NOT TESTED
   % print(gcf, strcat(new_name{1}, 'o'),'-dpng')
   % print(gcf, strcat(new_name{1}, 'p'),'-djpg')


   close(fig);
end