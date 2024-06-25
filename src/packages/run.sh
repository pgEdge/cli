fpm \
  -s dir -t rpm \
  -p pgedge-16.2.3.24.7.3.rpm \
  --name pgedge \
  --version 16.2.3.24.7.3 \
  --architecture aarch64 \
  --description "pgedge 16 bundle" \
  --url "https://pgedge.com" \
  --maintainer "support@pgedge.com" \
  --after-install after-install.sh \
  --no-rpm-autoreqprov \
  --rpm-tag '%define _build_id_links none' \
  --rpm-tag '%undefine _missing_build_ids_terminate_build' \
  --rpm-user pgedge \
  bundle-pg16.3-2-cli24.7.3-arm9/.=/opt/pgedge/.
