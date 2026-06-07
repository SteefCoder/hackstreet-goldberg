step(qr, i, j, s) -> (

    n = length(qr);
    m = length(qr:0);

    if(i >= n,
        write_file('baz', 'shared_text', 'A');
        // print('writing to baz...');
        run('player bob kill');
        return()
    );

    bot = player('bob');

    // snake direction per row
    dir = if(i % 2 == 0, 1, -1);

    // bot position follows snake pattern
    x = 20 + i;
    z = 80 + j;

    modify(bot, 'pos', x, -60, z);
    modify(bot, 'look', x, -61, z + dir);

    item = if(qr:i:j,
        'minecraft:black_concrete',
        'minecraft:white_concrete'
    );

    destroy(x, -61, z + 1);
    place_item(item, x, -61, z + 1);

    // move horizontally in snake pattern
    j += dir;

    // boundary handling
    if(j >= m,
        i += 1;
        j = m - 1
    );

    if(j < 0,
        i += 1;
        j = 0
    );

    if (s,
        step(qr, i, j, false);
        // schedule(1, 'step', qr, i, j, false);
        dir = if(i % 2 == 0, 1, -1);
        j += dir;

        // boundary handling
        if(j >= m,
            i += 1;
            j = m - 1
        );

        if(j < 0,
            i += 1;
            j = 0
        );
        step(qr, i, j, false);
        // schedule(1, 'step', qr, i, j, false);
        dir = if(i % 2 == 0, 1, -1);
        j += dir;

        // boundary handling
        if(j >= m,
            i += 1;
            j = m - 1
        );

        if(j < 0,
            i += 1;
            j = 0
        );
        schedule(0, 'step', qr, i, j, true);
    );
);


create_qr() -> (
    qr = read_file('qr', 'shared_json');
    // run('fill 20 -61 81 50 -61 121 minecraft:grass_block');
    
    step(qr, 0, 0, true);

);

