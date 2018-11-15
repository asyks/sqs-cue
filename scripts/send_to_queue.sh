#!/usr/bin/env bash

set -o errexit
set -o nounset

## defaults
DEFAULT_AWS_PROFILE=default
DEFAULT_MSG_GROUP_ID='default-message-group'

## output usage
usage () {
  printf "  usage: ./send_to_queue.sh <queue-url> [aws-profile]\n"
}

## output error
error () {
  {
    printf "error: %s\n" "${@}"
  } >&2
}

## create message body
create_msg_body() {
    key_val=`hexdump -n 16 -e '4/4 "%08X" 1 "\n"' /dev/random`
    name_val=`cat /dev/urandom | LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`

    msg_body='{"key": "'${key_val}'", "name": "'${name_val}'}"'
}

## create awscli arg string
create_arg_str() {
  arg_str='--queue-url '${queue_url}' --profile '${aws_profile}' '

  if [[ "${queue_url}" == *.fifo ]]; then
    arg_str=${arg_str}' --message-group-id '${DEFAULT_MSG_GROUP_ID}' '
  fi
}

## send message(s) to sqs
main () {
  queue_url="${1:-}"
  aws_profile="${2:-${DEFAULT_AWS_PROFILE}}"
  shift

  if [[ -z "${queue_url}" ]]; then
    error "Must specify queue_url"
    usage
    return 2
  fi

  create_msg_body
  create_arg_str

  aws sqs send-message ${arg_str} --message-body "${msg_body}"

  return 0
}

main "${@:-}"
exit $?
