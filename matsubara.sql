INSERT INTO family( f_id, f_name )
    VALUES( "matsubara", "松原家" );

INSERT into users(
    u_id, u_name, f_id, score, admin, adult, sex
    ) VALUES (
    %s,%s,%s,%s,%s,%s,%s)"