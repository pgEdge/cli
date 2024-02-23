  SELECT DISTINCT p.image_file, r.sort_order, r.project, r.disp_name as rel_name,
         v.version, p.sources_url, p.project_url, v.platform, 
         v.is_current, v.release_date as rel_date, p.description as proj_desc, 
         r.description as rel_desc
    FROM projects p, releases r, versions v
   WHERE p.project = r.project
     AND r.component = v.component
     AND is_current = 1 AND stage = 'prod'
     AND parent in ('', 'pg16')
order by 2;
