SELECT
    pgr_createTopology(
        'reach.edge_segments',
        0.001,
        'geometry',
        'id',
        'source',
        'target',
        clean := TRUE
    );