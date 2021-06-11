FROM pandoc/ubuntu-latex:2.14.0.1

WORKDIR /app
ADD render-documentation.sh /app
RUN chmod +x /app/render-documentation.sh

ENTRYPOINT []
CMD ["/app/render-documentation.sh"]