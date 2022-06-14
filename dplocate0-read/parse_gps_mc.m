function parse_gps_mc(read_dir, out_dir, extension, matlab_dir)
display('START');
encp=1;

% Get passcode
if encp==1
    % Check extension
    if (strcmp(extension,'csv.lock') == 1 || strcmp(extension,'csv') == 1)
        extension = strcat('.',extension);
    end
    pss = getenv('BEIWE_STUDY_PASSCODE');
    if (strcmp(extension,'.csv.lock') == 1 && isempty(pss) == 1)
        disp('Please set the BEIWE_STUDY_PASSCODE environment variable.');
        disp('Cannot unlock files without the passphrase.Exiting.');
        exit(1);
    end
end

% Check if the path is properly formatted
if ~ endsWith(read_dir, '/')
    read_dir = strcat(read_dir, '/');
end

if ~ endsWith(out_dir, '/')
    out_dir = strcat(out_dir, '/');
end

if ~ endsWith(matlab_dir, '/')
    matlab_dir = strcat(matlab_dir, '/');
end

% Check if the path exists
if exist(read_dir,'dir')~=7
    disp(strcat('Input directory ', read_dir, ' does not exist. Exiting.'));
    exit(1);
end

if exist(out_dir,'dir')~=7
    disp(strcat('Output directory ', out_dir, ' does not exist. Exiting.'));
    exit(1);
end

% Initialization
t1=[]; lat1=[]; lon1=[]; alt1=[]; acc1=[];  tjdmx=0;

% Check output directory
output_filepath_mat = strcat(out_dir, 'gps_dash2/file_gps.mat');
if (exist(output_filepath_mat, 'file') == 2)
    disp('Previous file exists.');
    if encp==1
        tmpN = tempname('/tmp');
        temp_unlocked_m=strcat(tmpN,'.mat');
        cmd = sprintf('python %sparse_gps_decrypter.py --input "%s" --output "%s"', matlab_dir, output_filepath_mat, temp_unlocked_m);
        disp(cmd);
        system(cmd);
        load(temp_unlocked_m)
        if (exist(temp_unlocked_m)==2)
            delete(temp_unlocked_m);
        else
            disp(strcat(temp_unlocked_m, ' does not exist!'));
        end
    end
    tjmx=max(t1);
    tjdmx=1000*3600*floor(tjmx/1000/3600);
    tmdmx=datevec(tjdmx/1000/3600/24+datenum('1970-01-01'));
    [length(t1) length(lat1) length(lon1) length(alt1) length(acc1)];
    t1=t1(t1<tjdmx);
   % u1=u1(t1<tjdmx);
    lat1=lat1(t1<tjdmx);
    lon1=lon1(t1<tjdmx);
    alt1=alt1(t1<tjdmx);
    acc1=acc1(t1<tjdmx);
end
% Initialization
disp('Parameters checked. READING GPS files.');
mind_path = strcat(read_dir,'/gps/');
mind_files = dir(strcat(mind_path, '*.json'));
files_len = length(mind_files)
if files_len == 0
    display('Files do not exist under this directory.');
end

file_path = strcat(mind_path,mind_files(end,1).name)
%% %%%%%%% Encryption Bypassed %%%%%%%%%%%%%%%%%%
if encp==1
    % Handle locked and unlocked files
    if strcmp(extension,'.csv') == 1
        temp_parsed=file_path;
    elseif strcmp(extension,'.csv.lock') == 1
        cmd = sprintf('python %sparse_gps_decrypter.py --input "%s" --output "%s"', matlab_dir, file_path, temp_unlocked);
        disp(cmd);
        system(cmd);
        if (exist(temp_unlocked)==2)
            temp_parsed=temp_unlocked;
        else
            disp('File unlock unsuccessful. Moving onto the next file');
        end
    else
        disp('Unsupported file extension');
    end
end
%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
str = fileread(file_path); % dedicated for reading files as text
% Aggregate GPS data
dt = jsondecode(str); % Using the jsondecode function to parse JSON from string
dt1=dt;

%% %%%%%%%%%%%%%%%% Parse Data %%%%%%%%%%%%%
t=[];  lat=[]; lon=[]; alt=[]; acc=[];
for i=1:length(dt1)
    sns=dt1(i).sensor;
    tm=dt1(i).timestamp;

    igps=strcmp(sns,'lamp.gps');
    if igps==1
        t=[t;tm];
        lat=[lat;dt1(i).data.latitude];
        lon=[lon;dt1(i).data.longitude];
        alt=[alt;dt1(i).data.altitude];
        acc=[acc;dt1(i).data.accuracy];
    end
end

t1=[t1;t]; lat1=[lat1;lat]; lon1=[lon1;lon];
alt1=[alt1;alt]; acc1=[acc1;acc];

% Save data as mat file
disp(strcat('Saving file file_gps.mat'));
if exist(strcat(out_dir,'gps_dash2'),'dir')~=7
    mkdir(strcat(out_dir,'gps_dash2'));
end
if encp==1
    save(input_mat_file,'t1','u1','lat1','lon1','alt1','acc1','-v7.3');
    % Encrypt file
    disp(strcat('Encrypting file ', output_filepath_mat));
    cmd = sprintf('python %sparse_gps_encrypter.py --input "%s" --output "%s"', matlab_dir, input_mat_file, output_filepath_mat);
    system(cmd);
    delete(input_mat_file);
else
    save(output_filepath_mat,'lat1','lon1','alt1','acc1','t1','-v7.3')
end

display('COMPLETE');
exit(0);
