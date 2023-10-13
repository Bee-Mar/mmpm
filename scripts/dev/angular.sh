#!/bin/bash

runtime=$( [[ $(command -v bun) ]] && echo 'bun' || echo 'npm' )

cd web && $runtime run serve
