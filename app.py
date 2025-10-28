

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)