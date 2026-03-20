q_sms_ca = sln_results.DatasetSMSCA * proj(sln_cell.Cell, 'cell_unid', 'file_name', 'source_id') * sln_cell.CellName * proj(sln_cell.AssignType.current, 'cell_type', 'cell_unid') *...
proj(sln_symphony.ExperimentRetina, 'source_id -> retina_id', 'animal_id', 'side', 'orientation') ...
* sln_symphony.UserParamAnimalFeedingCondition * sln_cell.RetinaQuadrant & 'file_name LIKE "____26_" and (feeding_condition = "chow" or feeding_condition = "HFD")'
sms_ca_dataset = fetch(q_sms_ca, '*');

var_names_to_rm = {'psth_x', 'sms_psth', ...
    'online_type', ...
    'git_tag', ...
    'event_id', 'entry_time','user_name'}


new_struct = rmfield(sms_ca_dataset, var_names_to_rm);

var_names = fieldnames(new_struct);

T = struct();

for i = 1:length(new_struct)
    struct_var_length = zeros(length(var_names), 1);
    % the code is ugly but idgaf
    for name = 1 : length(var_names)
        struct_var_length(name) = size(new_struct(i).(var_names{name}),1);
    end
    wide_var = var_names(find(struct_var_length > 1));
    n_row_to_melt = max(struct_var_length);
    
    t_temp = table();
    last_row = size(T, 2);
    for name = 1 : length(var_names)
        var = var_names{name};
        for j = 1 : n_row_to_melt
            if ismember(var, wide_var)
                T(last_row + j).(var) = new_struct(i).(var)(j);
            else
                T(last_row + j).(var) = new_struct(i).(var);
            end
            T(last_row +j).dataset_number = i;
        end
    end

    
    

end